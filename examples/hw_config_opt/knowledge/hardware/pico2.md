# Raspberry Pi Pico 2 (RP2350) — Hardware Facts and Valid Knobs

> Source: `RP-008299-DS-2-pico-2-datasheet.pdf` (Raspberry Pi Ltd, build 2026-03-12). PDF never referenced at runtime.

## Hardware facts

- **MCU**: RP2350A (dual-core, selectable at boot: **2× Arm Cortex-M33** *or* **2× RISC-V Hazard3**)
- **Core clock**: rated **up to 150 MHz** (on-chip PLL, variable core frequency) — up from 133 MHz on original Pico/RP2040. This harness permits tuning up to **250 MHz** (see the valid-knob table); 150–250 MHz is above the datasheet's rated max (an overclock), so verify stability/thermals on your board.
- **SRAM**: 520 kB multi-bank high-performance SRAM
- **Flash**: 4 MB external QSPI (Winbond W25Q32RV) with XIP + 16 kB on-chip cache
- **NPU/SIMD**: none — no hardware NN accelerator, no SIMD extensions; TFLite Micro runs on scalar CPU only
- **GPIO**: 26 exposed of 30 total RP2350 GPIO, fixed 3.3 V IO voltage (not user-selectable, unlike RP2350's native 1.8–3.3 V range)
- **ADC**: 12-bit, 500 ksps, 4 channels available on-chip (3 exposed on header: GP26–28; GP29 used internally)
- **PIO**: 3 blocks / 12 state machines total (up from 2 blocks / 8 on original Pico)
- **Security features** (not relevant to our workloads but present): TrustZone-M, signed boot, 8 kB antifuse OTP, SHA-256 accel, HW TRNG — not used in current harness
- **Operating temp**: -20 °C to 85 °C (incl. self-heating); recommended max ambient 70 °C

## Runtime

- **SDK**: Pico C/C++ SDK or MicroPython. Our harness uses **TFLite Micro** compiled against the Pico SDK (C/C++), flashed as `.uf2`.
- **No RTOS assumption** — bare-metal loop unless project explicitly adds FreeRTOS-SMP (not currently in stack).
- **Dual-core note**: TFLite Micro inference in our harness is expected **single-core** (core 1 idle) unless a config explicitly enables multicore dispatch — flag any knob that claims multicore speedup, since our current `GeneratedHarness.evaluate()` does not orchestrate cross-core sync.
- **Forbidden/inapplicable libs**: no HailoRT, no TensorRT, no DCGM — those are for the NPU/Jetson/DGX branches. Do not let the config-gen agent inject NPU-oriented knobs (e.g. `hailo_batch_size`) for this device.
- **Flashing path**: USB Mass Storage (BOOTSEL) drag-and-drop `.uf2`, or SWD (no button press required — **this is the automatable path**, see Pitfalls).

## Valid knobs (authoritative allowlist)


| knob | type | range / allowed values | default | notes |
|---|---|---|---|---|
| `freq_mhz` | int | **48-250** | 150 | Confirmed tunable range for this board/harness. Note the upper half is an **overclock**: the RP2350 datasheet only rates the PLL "up to 150 MHz", so 150–250 MHz exceeds the datasheet spec — validate stability and thermals on your unit. Runtime-settable via the SDK clock API; higher = lower latency, higher power. |
| `sleep_mode` | int | `0`, `1`, `2`, `3` | `0` | Runtime low-power mode, applied over serial after power-on (resets to the firmware default on every power cycle). `0`=baseline, `1`=run-idle (`__wfe`), `2`=sleep_en gated (PLLs on), `3`=sleep_en gated + XOSC. The firmware rejects any value outside 0–3. Modes 2/3 briefly drop and re-enumerate USB during the sleep window. This is the real runtime power knob the harness implements. |
| `opt` | str | `O0`, `O2`, `O3`, `Os` | `O2` | Compiler optimization level. Not a hardware fact — the datasheet says nothing about this — but it's a legitimate build-time knob if your toolchain supports it. **BUILD-TIME**: changing it forces a full rebuild + reflash, unlike `freq_mhz`/`sleep_mode` which are runtime-settable. Confirm against your actual CMake/build config before trusting the exact flag set. |

## Not wired into the current harness — do NOT emit these

The RP2350 datasheet exposes other controls, but the firmware + PPK2 pipeline
have no path to apply them, so the evaluator REJECTS them as unknown knobs.
They are documented here only so the agent knows *not* to emit them:

- `smps_mode` (`pfm`/`pwm`, GPIO23 / RT6150 SMPS power-save pin): a real RP2350
  feature, but nothing in `flash_device.py`/`power_test.py` sets it.
- `active_cores` (`1`/`2`, multicore dispatch): the harness runs single-core
  only — `GeneratedHarness.evaluate()` does not orchestrate cross-core sync.

## Known pitfalls
- `freq_mhz` and `sleep_mode` reset to the firmware default on every power cycle;
  the pipeline re-applies them after power-on, before the capture starts.
- `opt` is the expensive knob: every distinct value forces a rebuild+reflash, so
  the agent mutating it costs minutes per attempt. Prefer exploring `freq_mhz`
  and `sleep_mode` (runtime) before `opt`.
- The `performance`-style tradeoff: max `freq_mhz` gives lowest latency but
  usually worst energy-per-inference. Look for the knee, not the extreme.

## Accuracy
- These knobs do NOT change model outputs, so accuracy is fixed per model +
  workload. It is looked up from accuracy_table.py and enforced as a floor by
  the evaluator, never measured on-device here.
- See knowledge/constraints/measurement.md for the measurement contract.
