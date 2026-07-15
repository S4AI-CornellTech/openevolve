"""
Given a device + workload, it:
  1. loads config.yaml
  2. injects that device's hardware knowledge (knowledge/hardware/<device>.md +
     all constraints) into the LLM system_message
  3. tells the evaluator which device/workload to measure (via env vars)
  4. runs OpenEvolve

To use it: 
    export OPENAI_API_KEY="<your-gemini-key>"
    python run_task.py --device pico2 --workload kws_small --iterations 30
    # add --mock to run the whole loop offline with synthetic metrics (no board)
"""

import argparse
import os

from openevolve import run_evolution
from openevolve.config import load_config

HERE = os.path.dirname(os.path.abspath(__file__))


def build_system_message(device, workload):
    """Assemble the per-device system prompt: hardware facts + valid-knob table +
    constraints"""
    parts = [
        f"""You are an expert embedded-systems performance engineer tuning the
runtime configuration of the {device} while it runs the {workload} ML
inference workload. Your objective is to find knob settings that MINIMIZE
energy per inference (mJ) and latency per inference (ms) while keeping accuracy
at or above the fixed floor.

# WHAT YOU EDIT
You edit ONLY the values in the `CONFIG` dict inside the EVOLVE-BLOCK of the
program. You do not change the dict's shape, add keys, or touch any code
outside the block. Every key you emit MUST appear in this device's valid-knob
table below; the evaluator REJECTS any unknown key, so an invented knob wastes
the whole attempt.

# OPTIMIZATION STRATEGY
1. Energy and latency usually TRADE OFF. The lowest-latency setting (e.g. max
   frequency) is often the worst on energy-per-inference. Hunt for the KNEE of
   the curve, not the extreme.
2. Prefer cheap RUNTIME knobs first. Knobs applied over serial after power-on
   (e.g. frequency, sleep mode) cost seconds to try. BUILD-TIME knobs (e.g.
   compiler optimization) force a rebuild+reflash and cost minutes — change
   them only once the cheap axes are well explored, and change one at a time.
3. Sleep / low-power modes cut idle energy but can add wake latency; frequency
   scaling trades power against speed. Reason about which dominates for THIS
   workload before proposing a value.
4. Move deliberately: change ONE knob per step when possible so the measured
   history stays interpretable. Don't jump to an untested extreme.

# HOW TO USE THE MEASURED HISTORY
The prompt includes prior configs with their MEASURED energy/latency/score from
real hardware. Trust those numbers — a trusted wrapper produced them, not the
candidate. Read the trend, form a hypothesis ("lowering freq_mhz from 150 to
100 cut energy X% for Y% more latency"), and propose the config that best
advances the energy x latency frontier. Repeating a config already in the
history learns nothing.

# HARD RULES
- Emit ONLY knob values from the valid-knob table. No invented knobs.
- NEVER add energy, latency, accuracy, score, or any metric field — self-
  reported metrics are discarded as invalid. Selection is your job; scoring is
  the wrapper's.
- Stay within each knob's stated range/allowed values and respect any device
  note marking a knob build-time, single-core-only, or not-wired.
- Keep accuracy above the floor. These knobs don't change model outputs, so
  accuracy is fixed and looked up — but a knob the device can't sustain (e.g.
  an unsupported frequency) still counts as a failed attempt.
"""
    ]

    kb = os.path.join(HERE, "knowledge", "hardware", f"{device}.md")
    if os.path.exists(kb):
        with open(kb) as f:
            parts.append(f"## DEVICE FACTS AND VALID KNOBS ({device})\n\n{f.read()}")
    else:
        parts.append(
            f"## DEVICE FACTS AND VALID KNOBS ({device})\n\n"
            f"(WARNING: knowledge/hardware/{device}.md is missing.)"
        )

    constraints_dir = os.path.join(HERE, "knowledge", "constraints")
    if os.path.isdir(constraints_dir):
        chunks = []
        for name in sorted(os.listdir(constraints_dir)):
            if name.endswith(".md"):
                with open(os.path.join(constraints_dir, name)) as f:
                    chunks.append(f.read())
        if chunks:
            parts.append("## CONSTRAINTS\n\n" + "\n\n".join(chunks))

    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="pico2") # parsed into args.device
    ap.add_argument("--workload", default="kws_small")
    ap.add_argument("--iterations", type=int, default=30)
    ap.add_argument("--mock", action="store_true",
                    help="run the loop with synthetic metrics (no hardware)")
    ap.add_argument("--output", default=os.path.join(HERE, "openevolve_output"),
                    help="where to persist checkpoints, per-program JSON (metrics + "
                         "the exact prompts), and the best program")
    args = ap.parse_args()

    config = load_config(os.path.join(HERE, "config.yaml"))
    config.prompt.system_message = build_system_message(args.device, args.workload)

    # Tell the evaluator which device/workload to measure. Set in the parent
    # process so every worker inherits them.
    os.environ["HW_CONFIG_DEVICE"] = args.device
    os.environ["HW_CONFIG_WORKLOAD"] = args.workload
    if args.mock:
        os.environ["HW_CONFIG_MOCK"] = "1"

    result = run_evolution(
        initial_program=os.path.join(HERE, "initial_program.py"),
        evaluator=os.path.join(HERE, "evaluator.py"),
        config=config,
        iterations=args.iterations,
        output_dir=args.output, # Results recorded: keeps checkpoints/programs/prompts on disk
        cleanup=False,
    )
    print("\nBest program metrics:", result.best_program.metrics if result.best_program else None)
    print(f"Results saved under: {args.output}")
    print(f"  per-program JSON (metrics + exact prompts): {os.path.join(args.output, 'checkpoints')}")
    print(f"  best program:                               {os.path.join(args.output, 'best')}")


if __name__ == "__main__":
    main()
