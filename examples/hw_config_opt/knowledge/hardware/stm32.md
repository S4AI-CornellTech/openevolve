# STM32 — Hardware Facts and Valid Knobs

## Hardware facts
- MCU: STM32 Arm Cortex-M family (exact part/clock depends on the board in the rig)
- No NPU on classic parts; inference on the CPU (CMSIS-NN / X-CUBE-AI kernels)
- Toolchain: STM32CubeIDE / arm-none-eabi

> TODO: fill in the exact STM32 part, core (e.g. M4F/M7), max clock, SRAM/flash
> for the board actually in your measurement rig before trusting these facts.

## Runtime
- Fixed C firmware; no on-device Python. GPIO marker pin around inference.
- **MANUAL REWIRE REQUIRED.** In HUB_MANUAL_REWIRE — the pipeline pauses for a
  physical wire move mid-run, so it CANNOT run unattended (an evolution run will
  block on human input). Manual measurement only until the rig is changed.

## Valid knobs
**(none exposed in the PPK2 pipeline yet.)** Measure-only at firmware defaults.

| knob | type | range / allowed values | notes |
|------|------|------------------------|-------|
| (none yet) | | | firmware-default measurement only; manual-rewire device |

## Accuracy
- Fixed per model+workload; looked up from accuracy_table.py, enforced as a
  floor. See constraints/measurement.md.
