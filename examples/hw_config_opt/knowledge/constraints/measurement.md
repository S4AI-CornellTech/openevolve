# Measurement Contract

Measurement is **externally owned**. The agent proposes configs; it never
measures, scores, or judges them.

- **A trusted wrapper owns all metrics.** Energy (mJ/inference) and latency
  (ms/inference) come only from the PPK2 power pipeline after it flashes a config
  to the physical device and captures the GPIO-marked inference window.
- **Accuracy is fixed and external.** The knobs in this task (frequency,
  compiler optimization, sleep mode) do not change model outputs, so accuracy is
  a constant per model + workload, measured once offline against a held-out
  labelled set and looked up from accuracy_table.py. The agent never computes it.
- **Self-reported metrics are rejected.** A config that includes energy/latency/
  accuracy fields is discarded as invalid. Emit only knob values.
- **The agent's job is selection, not scoring.** Use the measured history in the
  prompt to choose the next config; trust the numbers because the wrapper
  produced them, not the candidate.
