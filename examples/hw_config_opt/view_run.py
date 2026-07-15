"""
Flatten an OpenEvolve checkpoint into a readable, iteration-ordered report.

The per-program JSON files under
openevolve_output/checkpoints/checkpoint_*/programs/*.json contain everything
(evolved CONFIG, metrics, the exact prompt, and the LLM's response) but with
escaped newlines that are painful to read raw. This script unpacks them into a
Markdown file (and/or stdout) sorted by iteration.

Usage:
    python view_run.py                         # latest checkpoint -> run_readable.md
    python view_run.py --checkpoint openevolve_output/checkpoints/checkpoint_10
    python view_run.py --prompts               # also include the full system+user prompt
    python view_run.py --stdout                # print instead of writing a file
"""

import argparse
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def latest_checkpoint():
    ckpts = glob.glob(os.path.join(HERE, "openevolve_output", "checkpoints", "checkpoint_*"))
    if not ckpts:
        return None
    # checkpoint_<N> -> sort by N
    return max(ckpts, key=lambda p: int(p.rsplit("_", 1)[-1]))


def load_programs(checkpoint_dir):
    programs = []
    for path in glob.glob(os.path.join(checkpoint_dir, "programs", "*.json")):
        with open(path) as f:
            programs.append(json.load(f))
    # Order by the iteration the program was found (fall back to generation/timestamp)
    programs.sort(key=lambda d: (d.get("iteration_found", 0), d.get("generation", 0), d.get("timestamp", 0)))
    return programs


def fmt_metrics(m):
    if not m:
        return "(no metrics)"
    order = ["combined_score", "energy_mj", "latency_ms", "accuracy", "valid"]
    keys = [k for k in order if k in m] + [k for k in m if k not in order]
    return ", ".join(f"{k}={m[k]}" for k in keys)


def render(programs, best_id, include_prompts):
    lines = []
    for p in programs:
        star = "  ⭐ BEST" if p.get("id") == best_id else ""
        lines.append(f"## Iteration {p.get('iteration_found', '?')}{star}")
        lines.append(f"- id: `{p.get('id')}`  parent: `{p.get('parent_id')}`")
        lines.append(f"- metrics: {fmt_metrics(p.get('metrics'))}")
        if p.get("changes_description"):
            lines.append(f"- changes: {p['changes_description']}")

        lines.append("\n**Evolved CONFIG**\n")
        lines.append("```python\n" + (p.get("code") or "").strip() + "\n```")

        prompts = p.get("prompts") or {}
        for template_key, blk in prompts.items():
            responses = blk.get("responses") or []
            if responses:
                lines.append(f"\n**LLM response** ({template_key})\n")
                lines.append("```\n" + responses[0].strip() + "\n```")
            if include_prompts:
                lines.append(f"\n<details><summary>Prompt ({template_key})</summary>\n")
                lines.append("**System**\n\n```\n" + (blk.get("system") or "").strip() + "\n```")
                lines.append("\n**User**\n\n```\n" + (blk.get("user") or "").strip() + "\n```")
                lines.append("\n</details>")

        lines.append("\n---\n")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=None,
                    help="checkpoint dir (default: latest under openevolve_output/checkpoints)")
    ap.add_argument("--prompts", action="store_true",
                    help="also include the full system+user prompt (long)")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing a file")
    ap.add_argument("--output", default=os.path.join(HERE, "run_readable.md"))
    args = ap.parse_args()

    checkpoint = args.checkpoint or latest_checkpoint()
    if not checkpoint or not os.path.isdir(checkpoint):
        raise SystemExit(f"No checkpoint found (looked for {checkpoint!r}).")

    programs = load_programs(checkpoint)

    # The best program id is recorded in the checkpoint metadata if present.
    best_id = None
    meta_path = os.path.join(checkpoint, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            best_id = json.load(f).get("best_program_id")

    header = (
        f"# Evolution run — {os.path.basename(checkpoint)}\n\n"
        f"{len(programs)} programs, ordered by iteration. "
        f"Best (highest combined_score) marked ⭐.\n\n---\n"
    )
    report = header + render(programs, best_id, args.prompts)

    if args.stdout:
        print(report)
    else:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Wrote {args.output}  ({len(programs)} programs from {os.path.basename(checkpoint)})")


if __name__ == "__main__":
    main()
