# ESP32-S3 — Hardware Facts and Valid Knobs

## Hardware facts
- MCU: Xtensa LX7, dual-core, up to 240 MHz; Wi-Fi + BLE
- Adds vector (SIMD-like) instructions that accelerate int8 NN kernels vs. ESP32
- 512 KB SRAM (+ optional PSRAM); external SPI flash
- Toolchain: ESP-IDF; flashed over the serial port

## Runtime
- Fixed C firmware; no on-device Python. GPIO marker pin around inference.
- Hub port OFF during capture (HUB_OFF_FOR_MEASURE).

## Valid knobs
**(none exposed in the PPK2 pipeline yet.)** Measure-only at firmware defaults
until knobs are added here and to evaluator.VALID_KNOBS["esp32s3"].

| knob | type | range / allowed values | notes |
|------|------|------------------------|-------|
| (none yet) | | | firmware-default measurement only |

## Accuracy
- Fixed per model+workload; looked up from accuracy_table.py, enforced as a
  floor. See constraints/measurement.md.
