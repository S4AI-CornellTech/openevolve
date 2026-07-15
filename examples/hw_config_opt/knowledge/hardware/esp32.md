# ESP32 (original) — Hardware Facts and Valid Knobs

## Hardware facts
- MCU: Xtensa LX6, dual-core, up to 240 MHz; Wi-Fi + Bluetooth Classic/BLE
- 520 KB SRAM; external SPI flash
- No NPU; inference runs on CPU (TFLite Micro / ESP-NN kernels)
- Toolchain: ESP-IDF; firmware flashed over the serial (UART) port

## Runtime
- Fixed C firmware; no on-device Python. GPIO marker pin toggled around inference.
- Measurement requires the hub port OFF during capture (see HUB_OFF_FOR_MEASURE).

## Valid knobs
**(none exposed in the PPK2 pipeline yet.)** The current pipeline does not apply
freq/opt/sleep knobs on this device — it measures at firmware defaults only.
Add knobs here (and to evaluator.VALID_KNOBS["esp32"]) once the firmware exposes
them; until then this device is measure-only, not tunable.

| knob | type | range / allowed values | notes |
|------|------|------------------------|-------|
| (none yet) | | | firmware-default measurement only |

## Accuracy
- Fixed per model+workload; looked up from accuracy_table.py, enforced as a
  floor. See constraints/measurement.md.
