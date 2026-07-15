# ESP32-C6 — Hardware Facts and Valid Knobs

## Hardware facts
- MCU: single-core RISC-V, up to 160 MHz; Wi-Fi 6 + BLE + 802.15.4 (Zigbee/Thread)
- 512 KB SRAM; external SPI flash
- No NPU; inference on the RISC-V core (TFLite Micro kernels)
- Toolchain: ESP-IDF; flashed over the serial port

## Runtime
- Fixed C firmware; no on-device Python. GPIO marker pin around inference.
- Hub port OFF during capture (HUB_OFF_FOR_MEASURE).

## Valid knobs
**(none exposed in the PPK2 pipeline yet.)** Measure-only at firmware defaults
until knobs are added here and to evaluator.VALID_KNOBS["esp32c6"].

| knob | type | range / allowed values | notes |
|------|------|------------------------|-------|
| (none yet) | | | firmware-default measurement only |

## Accuracy
- Fixed per model+workload; looked up from accuracy_table.py, enforced as a
  floor. See constraints/measurement.md.
