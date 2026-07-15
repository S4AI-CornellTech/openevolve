# Nordic nRF52840 — Hardware Facts and Valid Knobs

## Hardware facts
- MCU: Cortex-M4F, 64 MHz; Bluetooth LE / 802.15.4
- 256 KB SRAM, 1 MB flash
- No NPU; inference on the M4F core (CMSIS-NN kernels)
- Toolchain: nRF Connect SDK / Zephyr

## Runtime
- Fixed C firmware; no on-device Python. GPIO marker pin around inference.
- **MANUAL REWIRE REQUIRED.** This device is in HUB_MANUAL_REWIRE: the pipeline
  pauses and prompts you to physically move the measurement wires mid-run. It
  therefore CANNOT run unattended — an evolution run will block on human input.
  Use it for one-off manual measurements, not automated search, until the rig
  is changed.

## Valid knobs
**(none exposed in the PPK2 pipeline yet.)** Measure-only at firmware defaults.

| knob | type | range / allowed values | notes |
|------|------|------------------------|-------|
| (none yet) | | | firmware-default measurement only; manual-rewire device |

## Accuracy
- Fixed per model+workload; looked up from accuracy_table.py, enforced as a
  floor. See constraints/measurement.md.
