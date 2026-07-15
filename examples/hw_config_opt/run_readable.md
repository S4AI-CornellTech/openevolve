# Evolution run — checkpoint_10

11 programs, ordered by iteration. Best (highest combined_score) marked ⭐.

---
## Iteration 0
- id: `adf74a7a-6520-4036-974a-d793d9c6d1aa`  parent: `None`
- metrics: combined_score=0.5081596275005497, energy_mj=0.0641, latency_ms=12.062, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
```

---

## Iteration 1
- id: `4085e187-7541-426b-b664-c8b8bfea06c5`  parent: `adf74a7a-6520-4036-974a-d793d9c6d1aa`
- metrics: combined_score=0.5148721065727875, energy_mj=0.0491, latency_ms=12.064, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power; latency should be unaffected
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
Looking at the single data point (freq=150, opt=O2, sleep=0 → energy=0.0641mJ, latency=12.06ms), I should explore the cheap runtime knobs before touching build-time `opt`. Since `sleep_mode` is a runtime knob that can reduce idle/waiting power without necessarily hurting inference latency, I'll test `sleep_mode=1` (run-idle `__wfe`) first, keeping frequency fixed to isolate its effect per the "one knob at a time" guidance.

<<<<<<< SEARCH
CONFIG = {
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 0,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
}
=======
CONFIG = {
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power; latency should be unaffected
}
>>>>>>> REPLACE
```

---

## Iteration 2
- id: `1201a33c-bc5e-4637-92d0-450530e1f0b4`  parent: `adf74a7a-6520-4036-974a-d793d9c6d1aa`
- metrics: combined_score=0.5150318851797012, energy_mj=0.0488, latency_ms=12.056000000000001, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power without USB re-enum cost
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
Looking at the history, only one config has been tested (the default). Since sleep_mode and freq_mhz are cheap runtime knobs, I should explore those before touching the build-time `opt` knob. Let's try enabling `sleep_mode=1` (run-idle via `__wfe`) while keeping frequency fixed — this is a low-risk, single-knob change that should cut idle/wait power during inference gaps without much latency penalty, since it only gates the core during idle cycles (PLLs stay on, no USB re-enumeration like modes 2/3).

<<<<<<< SEARCH
CONFIG = {
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 0,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
}
=======
CONFIG = {
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power without USB re-enum cost
}
>>>>>>> REPLACE
```

---

## Iteration 3
- id: `a93c1d83-e22f-4824-b473-c716f8d7ba1e`  parent: `adf74a7a-6520-4036-974a-d793d9c6d1aa`
- metrics: combined_score=0.5150260195695576, energy_mj=0.0488, latency_ms=12.058, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "sleep_mode": 1,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
<<<<<<< SEARCH
    "sleep_mode": 0,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
=======
    "sleep_mode": 1,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
>>>>>>> REPLACE
```

---

## Iteration 4
- id: `85894712-d2c3-4e6e-a69e-553db81cfbdc`  parent: `4085e187-7541-426b-b664-c8b8bfea06c5`
- metrics: combined_score=0.5147535799006695, energy_mj=0.0492, latency_ms=12.089, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "sleep_mode": 2,     # sleep_en gated (PLLs on) - test deeper idle power cut vs mode 1
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
Looking at the history, sleep_mode=1 improved energy significantly (0.0641→0.0491) with no latency cost. Let's try sleep_mode=2, which adds PLL gating on top of run-idle, potentially cutting more idle power while latency should remain similar since inference is active-time compute, not idle time.

<<<<<<< SEARCH
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power; latency should be unaffected
=======
    "sleep_mode": 2,     # sleep_en gated (PLLs on) - test deeper idle power cut vs mode 1
>>>>>>> REPLACE
```

---

## Iteration 5
- id: `340640b0-ff21-4fb3-9e3a-936c993e8c29`  parent: `1201a33c-bc5e-4637-92d0-450530e1f0b4`
- metrics: combined_score=0.4824349875247831, energy_mj=0.0959, latency_ms=18.092, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "freq_mhz": 100,     # lower clock to test energy/latency knee vs 150MHz baseline
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # keep run-idle (__wfe) sleep mode from prior best result
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
<<<<<<< SEARCH
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power without USB re-enum cost
=======
    "freq_mhz": 100,     # lower clock to test energy/latency knee vs 150MHz baseline
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # keep run-idle (__wfe) sleep mode from prior best result
>>>>>>> REPLACE
```

---

## Iteration 6
- id: `64d6024f-74c9-4084-beac-5349ce51ad80`  parent: `a93c1d83-e22f-4824-b473-c716f8d7ba1e`
- metrics: combined_score=0.5022322648936478, energy_mj=0.0613, latency_ms=15.071, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "freq_mhz": 120,     # lower from 150 to test energy/latency knee (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
<<<<<<< SEARCH
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
=======
    "freq_mhz": 120,     # lower from 150 to test energy/latency knee (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
>>>>>>> REPLACE
```

---

## Iteration 7
- id: `22f95859-41dd-429c-b076-7b4a7446ebad`  parent: `adf74a7a-6520-4036-974a-d793d9c6d1aa`
- metrics: combined_score=0.5079453119774096, energy_mj=0.0644, latency_ms=12.09, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "sleep_mode": 3,     # sleep_en gated + XOSC - test deepest idle power cut vs modes 1/2
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
Looking at the history: sleep_mode 1 gave best score (0.5149, energy 0.0491, latency 12.064), mode 2 was close (0.5148, energy 0.0492, latency 12.089), mode 0 was worst (0.5082, energy 0.0641). This shows sleep modes reduce idle energy with minimal latency cost. Since mode 1 and 2 are both good, let's test mode 3 (deepest sleep, XOSC gated) to see if it pushes energy even lower, following the one-knob-at-a-time exploration strategy.

<<<<<<< SEARCH
    "sleep_mode": 0,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
=======
    "sleep_mode": 3,     # sleep_en gated + XOSC - test deepest idle power cut vs modes 1/2
>>>>>>> REPLACE
```

---

## Iteration 8  ⭐ BEST
- id: `bb9a53cf-10b7-4ebd-9957-4105f20fabd6`  parent: `1201a33c-bc5e-4637-92d0-450530e1f0b4`
- metrics: combined_score=0.5268603831380366, energy_mj=0.048, latency_ms=9.048, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "freq_mhz": 200,     # test above-rated overclock to see if latency/energy both improve further
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # keep run-idle (__wfe) sleep mode from best result so far
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
<<<<<<< SEARCH
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power without USB re-enum cost
=======
    "freq_mhz": 200,     # test above-rated overclock to see if latency/energy both improve further
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # keep run-idle (__wfe) sleep mode from best result so far
>>>>>>> REPLACE
```

---

## Iteration 9
- id: `3eaa9e89-51ed-4fb7-9bf0-cefed2c6d9c9`  parent: `64d6024f-74c9-4084-beac-5349ce51ad80`
- metrics: combined_score=0.5147873345272733, energy_mj=0.0491, latency_ms=12.093, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "freq_mhz": 150,     # revert to 150 (best measured so far) since 120 regressed both metrics
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 2,     # try sleep_en gated (PLLs on) to see if it cuts energy further than run-idle
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
<<<<<<< SEARCH
    "freq_mhz": 120,     # lower from 150 to test energy/latency knee (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # 0=baseline, 1=run-idle, 2=sleep_en, 3=sleep_en+XOSC (runtime)
=======
    "freq_mhz": 150,     # revert to 150 (best measured so far) since 120 regressed both metrics
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 2,     # try sleep_en gated (PLLs on) to see if it cuts energy further than run-idle
>>>>>>> REPLACE
```

---

## Iteration 10
- id: `69cd8749-168f-4291-896b-c38bdc1da239`  parent: `4085e187-7541-426b-b664-c8b8bfea06c5`
- metrics: combined_score=0.49200678966148165, energy_mj=0.0734, latency_ms=18.086000000000002, accuracy=1.0, valid=1.0

**Evolved CONFIG**

```python
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
    "freq_mhz": 100,     # lower from 150 to probe energy/latency knee at reduced clock
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # best sleep mode so far: run-idle (__wfe), no USB re-enum overhead
}
# EVOLVE-BLOCK-END


def get_config():
    """Return the knob dict the evaluator will apply. Kept outside the evolve
    block so its shape is stable; only the CONFIG values above evolve."""
    return CONFIG


if __name__ == "__main__":
    print(get_config())
```

**LLM response** (diff_user)

```
Looking at the history: `sleep_mode=1` is currently best (0.5149, energy=0.0491, latency=12.064), narrowly beating `sleep_mode=2` (0.5148) and clearly beating `sleep_mode=0` (0.5082) and `sleep_mode=3` (0.5079). The sleep-mode axis looks well explored now — mode 1 is the sweet spot (idle power cut without USB re-enumeration overhead that modes 2/3 incur).

Latency stays ~12.06-12.09ms across all sleep modes, meaning execution time is dominated by compute at 150MHz, not sleep behavior. Time to explore the untouched `freq_mhz` axis (still at default 150) while keeping the best sleep_mode=1. Since energy = power × time, and this MCU's active power scales roughly with frequency while runtime scales inversely, there's likely a frequency knee below 150 where energy drops. I'll test a moderate reduction (150→100 MHz) as a single-knob change to probe this before going more extreme.

<<<<<<< SEARCH
CONFIG = {
    "freq_mhz": 150,     # RP2350 default 150 MHz (runtime knob)
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # try run-idle (__wfe) to cut idle power; latency should be unaffected
}
=======
CONFIG = {
    "freq_mhz": 100,     # lower from 150 to probe energy/latency knee at reduced clock
    "opt": "O2",         # compiler optimization O3/O2/Os/O0 (build-time: rebuild+reflash)
    "sleep_mode": 1,     # best sleep mode so far: run-idle (__wfe), no USB re-enum overhead
}
>>>>>>> REPLACE
```

---
