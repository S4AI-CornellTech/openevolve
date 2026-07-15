"""
Starting configuration for the hardware-config-optimization task.

OpenEvolve evolves ONLY the CONFIG dict inside the EVOLVE-BLOCK below. The
evaluator reads CONFIG, applies it on the physical device via the PPK2 power
pipeline, and measures energy + latency per inference. Accuracy is a fixed
property of the model/workload (these knobs do not change model outputs), so it
is looked up and enforced as a floor rather than re-measured.

Valid knobs and ranges for each device live in
knowledge/hardware/<device>.md. The evaluator REJECTS any key not in that
device's valid-knob table, so the agent cannot invent knobs.

Seeded for: pico2 (Raspberry Pi Pico 2 / RP2350), workload kws_small.
"""

# EVOLVE-BLOCK-START
# The agent edits ONLY the values below. Keep keys within the device's valid
# knob table (see knowledge/hardware/pico2.md). Do not add metric fields.
CONFIG = {
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 0,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
