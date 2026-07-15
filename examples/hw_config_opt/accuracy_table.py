"""
Fixed accuracy per (device, workload).

Why a table instead of a measurement: the knobs this task evolves (CPU
frequency, compiler optimization, sleep mode) change energy and latency but NOT
the model's outputs, so accuracy is constant across every config the agent can
try. It is therefore a property of the deployed model + workload, measured once
offline (held-out labelled set) and looked up here, then enforced as a floor by
the evaluator.

If you later add model-level knobs (quantization, width, pruning) that DO change
outputs, accuracy stops being constant and must be measured live instead — that
needs firmware that streams per-clip predictions over serial, which the current
PPK2 pipeline does not do.

"""

import os

# (device, workload) -> held-out top-1 accuracy in [0, 1], or None if not yet measured.
ACCURACY = {
    ("pico2", "kws_small"): None,   
    ("pico2", "kws_large"): None,
    ("pico", "kws_small"): None,
    ("pico", "kws_large"): None,
}

# Used only when a (device, workload) entry is missing/None, so the loop is
# runnable before the table is filled. Set >= the floor so a placeholder never
# silently fails every candidate.
DEFAULT_ACCURACY = float(os.environ.get("HW_CONFIG_DEFAULT_ACC", "1.0"))


def lookup_accuracy(device, workload):
    """Return the fixed accuracy for (device, workload). Falls back to
    DEFAULT_ACCURACY (with a warning) when the entry is missing or a placeholder."""
    acc = ACCURACY.get((device, workload))
    if acc is None:
        print(
            f"[accuracy_table] WARNING: no measured accuracy for "
            f"({device!r}, {workload!r}); using DEFAULT_ACCURACY={DEFAULT_ACCURACY}. "
            f"Fill accuracy_table.ACCURACY before trusting the accuracy floor."
        )
        return DEFAULT_ACCURACY
    return float(acc)
