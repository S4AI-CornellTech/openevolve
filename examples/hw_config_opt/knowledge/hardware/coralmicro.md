# Coral Dev Board Micro — Hardware Facts and Valid Knobs

## Hardware facts
- SoC: NXP i.MX RT1176 — Cortex-M7 @ ~800 MHz + Cortex-M4 @ ~400 MHz
- On-board **Coral Edge TPU** for quantized (int8) TFLite inference
- 64 MB SDRAM, 128 MB flash
- Toolchain: coralmicro (FreeRTOS); flashed via the Coral flashtool

## Runtime
- Fixed C firmware; no on-device Python. GPIO marker pin around inference.
- Inference typically runs on the Edge TPU; models must be int8 + edgetpu-compiled.
  CPU-only fallback is much slower and much less energy-efficient.

## Valid knobs
**(none exposed in the PPK2 pipeline yet.)** Measure-only at firmware defaults
until knobs are added here and to evaluator.VALID_KNOBS["coralmicro"]. Plausible
future knobs: which core the pre/post-processing runs on, TPU vs. CPU delegate.

| knob | type | range / allowed values | notes |
|------|------|------------------------|-------|
| (none yet) | | | firmware-default measurement only |

## Accuracy
- Fixed per model+workload; looked up from accuracy_table.py, enforced as a
  floor. See constraints/measurement.md.
