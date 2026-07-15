# Raspberry Pi Pico (RP2040) — Hardware Facts and Valid Knobs

## Hardware facts
- MCU: RP2040, dual Cortex-M0+, default 125 MHz
- SRAM: 264 KB; on-board QSPI flash: 2 MB
- No NPU/TPU; ML inference runs on the CPU cores (CMSIS-NN / TFLite Micro kernels)
- Firmware is fixed C, flashed as a .uf2 over BOOTSEL mass-storage

## Runtime
- Model runs as flashed firmware; no OS, no on-device Python.
- The board toggles a GPIO marker pin around each inference for the PPK2.

## Valid knobs
Only keys in this table are legal (must match evaluator.VALID_KNOBS["pico"]).

| knob       | type | range / allowed values              | notes |
|------------|------|--------------------------------------|-------|
| freq_mhz   | int  | 48 - 250 (default 125) — VERIFY      | RP2040 CPU clock; applied at runtime after power-on. M0+ has no FPU, so DSP-heavy kernels are slower than on the Pico 2. Verify a safe overclock max on your board. |
| opt        | str  | O3 / O2 / Os / O0 (default O2)        | Compiler optimization. BUILD-TIME: rebuild + reflash on change (slow). |
| sleep_mode | int  | 0 / 1 / 2 / 3 (default 0)             | 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC. Runtime. |

Supply voltage is NOT a knob: the DUT rail is fixed at 3300 mV and hard-pinned in
the evaluator. A candidate that emits `voltage_mv` is rejected as an unknown knob.

## Known pitfalls
- RP2040 (M0+, no FPU) is slower than RP2350 on the same clock for float-heavy
  models; expect higher latency floors.
- `opt` changes are the expensive mutation (rebuild+reflash).
- `freq_mhz`/`sleep_mode` reset on each power cycle; re-applied before capture.

## Accuracy
- Fixed per model+workload (knobs don't change outputs). Looked up from
  accuracy_table.py and enforced as a floor. See constraints/measurement.md.
