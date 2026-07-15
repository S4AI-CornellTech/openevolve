# hw_config_opt — evolving hardware runtime configs for energy + latency

OpenEvolve task that evolves a device's **runtime configuration knobs** to
minimize energy-per-inference and latency-per-inference, subject to a fixed
accuracy floor. Measurement runs on real hardware through the PPK2 power
pipeline.

## What evolves vs. what's trusted

- **The agent (LLM) edits** the `CONFIG` knob dict in `initial_program.py` —
  *what* is tuned.
- **Trusted code owns *how* it's measured**: `evaluator.py` applies the config
  on the device via the PPK2 pipeline and reads back energy + latency. The
  candidate never times, powers, or scores itself.

## Files

| File | Role |
|------|------|
| `initial_program.py` | The evolving `CONFIG` (knobs) inside an EVOLVE-BLOCK |
| `evaluator.py` | OpenEvolve `evaluate()` → PPK2 measurement → metrics |
| `accuracy_table.py` | Fixed accuracy per (device, workload); enforced as a floor |
| `config.yaml` | OpenEvolve config: serial eval, energy×latency MAP-Elites grid |
| `run_task.py` | Launcher: injects `knowledge/hardware/<device>.md` into the prompt |
| `knowledge/hardware/*.md` | Per-device facts + valid-knob tables (the authoritative allowlist) |
| `knowledge/constraints/measurement.md` | The measurement contract |

## How the pieces connect

```
run_task.py  --device pico2 --workload kws_small
   │  injects knowledge/hardware/pico2.md into system_message
   │  sets HW_CONFIG_DEVICE / HW_CONFIG_WORKLOAD
   ▼
OpenEvolve engine (islands + MAP-Elites over energy_mj × latency_ms)
   │  LLM edits CONFIG in initial_program.py
   ▼
evaluator.evaluate(program_path)
   │  validate knobs → PPK2 run_measurement → energy_mj + latency_ms
   │  accuracy = accuracy_table.lookup(...)  (fixed; floor-gated)
   ▼
combined_score  (0 below floor; else higher for lower energy+latency)
```

## Run it

**Offline wiring test (no hardware, synthetic metrics):**
```bash
export OPENAI_API_KEY="<your-gemini-key>"
python run_task.py --device pico2 --workload kws_small --iterations 15 --mock
```

**Real measurement (PPK2 + board attached):**
```bash
export OPENAI_API_KEY="<your-gemini-key>"
export POWER_PIPELINE_DIR="/Users/katelynn/PycharmProjects/Power measurement pipeline"
python run_task.py --device pico2 --workload kws_small --iterations 30
```

## Important constraints (read before a real run)

- **Serial only.** One PPK2 + one USB hub → measurements cannot run in parallel.
  `config.yaml` pins `parallel_evaluations: 1`. Do not raise it.
- **Only pico / pico2 are tunable** in the current pipeline (knobs: `freq_mhz`,
  `opt`, `sleep_mode`). The other six devices are measure-only at firmware
  defaults until firmware exposes knobs — their knowledge files say so.
  Supply voltage is **not** a knob: the DUT rail is fixed at 3.3 V
  (`SUPPLY_VOLTAGE_MV = 3300` in `evaluator.py`) and a candidate emitting
  `voltage_mv` is rejected as an unknown knob.
- **nrf52 and stm32 need a human** to move wires mid-measurement, so they cannot
  run unattended. Don't launch automated evolution on them.
- **`opt` is expensive**: changing it forces a rebuild + reflash (minutes). The
  runtime knobs (`freq_mhz`, `sleep_mode`) are cheap by comparison.
- **Accuracy is a placeholder** until you fill `accuracy_table.ACCURACY` with
  real held-out numbers. Until then it defaults to 1.0 (passes the floor) and
  warns.

## Adding a device's knobs later
1. Add the knob names to `evaluator.VALID_KNOBS["<device>"]`.
2. Add them to the `## Valid knobs` table in `knowledge/hardware/<device>.md`.
3. Make sure `run_measurement` (in the PPK2 pipeline) actually applies them.
