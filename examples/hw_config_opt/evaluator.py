"""
OpenEvolve evaluator for the hardware-config-optimization task.

Contract: OpenEvolve calls evaluate(program_path) on each evolved candidate. The
candidate is a config module (see initial_program.py) exposing get_config() ->
knob dict. This evaluator:

  1. Loads the candidate and extracts its CONFIG knobs.
  2. Validates the knobs against the device's allowlist (rejects invented keys).
  3. Applies the config on the physical device and measures energy + latency via
     the PPK2 power pipeline (main.run_measurement -> results_summary.csv).
  4. Looks up the fixed accuracy for (device, workload) and gates on the floor.
  5. Returns metrics: combined_score (fitness), energy_mj + latency_ms
     (MAP-Elites features), accuracy, valid.

The agent writes WHAT is tuned (the knob values); this trusted code owns HOW it
is measured. Accuracy/energy/latency never come from the candidate.

Env:
  HW_CONFIG_DEVICE       device slug (default pico2). run_task.py sets this.
  HW_CONFIG_WORKLOAD     workload (default kws_small). run_task.py sets this.
  HW_CONFIG_ACC_FLOOR    accuracy floor (default 0.75).
  HW_CONFIG_MOCK         "1" to use the synthetic model instead of real hardware.
  POWER_PIPELINE_SSH     user@host of the remote rig (default s4ai@10.56.252.43).
  POWER_PIPELINE_REMOTE_DIR      remote pipeline checkout
                                 (default $HOME/power-measurement-pipeline).
  POWER_PIPELINE_TIMEOUT one measurement's SSH wall-clock budget in seconds
                         (default 540; keep < evaluator.timeout in config.yaml).
"""

import importlib.util
import os
import re
import shlex
import subprocess
import sys
import traceback

DEVICE = os.environ.get("HW_CONFIG_DEVICE", "pico2")
WORKLOAD = os.environ.get("HW_CONFIG_WORKLOAD", "kws_small")
ACCURACY_FLOOR = float(os.environ.get("HW_CONFIG_ACC_FLOOR", "0.75"))
MOCK = os.environ.get("HW_CONFIG_MOCK") == "1"
# The measurement rig is remote; the evaluator drives it over key-based SSH.
SSH_HOST = os.environ.get("POWER_PIPELINE_SSH", "s4ai@10.56.252.43")
REMOTE_DIR = os.environ.get("POWER_PIPELINE_REMOTE_DIR", "$HOME/power-measurement-pipeline")
REMOTE_TIMEOUT = int(os.environ.get("POWER_PIPELINE_TIMEOUT", "540"))

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from accuracy_table import lookup_accuracy  # noqa: E402

# Live log of the current remote measurement, so a long build/flash is watchable:
#   tail -f examples/hw_config_opt/measure_live.log
# Truncated at the start of every measurement (measurement is serial), so it always
# shows whatever is building right now. Override with HW_CONFIG_LIVE_LOG.
LIVE_LOG = os.environ.get("HW_CONFIG_LIVE_LOG", os.path.join(HERE, "measure_live.log"))

# Authoritative knob allowlist per device. MUST stay in sync with the
# "## Valid knobs" table in knowledge/hardware/<device>.md. Only pico/pico2
# expose runtime knobs in the current PPK2 pipeline.
VALID_KNOBS = {
    "pico2": {"freq_mhz", "opt", "sleep_mode"},
    "pico": {"freq_mhz", "opt", "sleep_mode"},
}
SUPPLY_VOLTAGE_MV = 3300
KNOB_RANGES = {
    "pico2": {"freq_mhz": (48, 250)},
    "pico": {"freq_mhz": (48, 250)},
}
# Discrete allowed values for enum-like knobs. Mirrors the valid-knob tables in
# knowledge/hardware/<device>.md so a bad value (e.g. sleep_mode=5, opt="O5") is
# rejected at validation instead of after a wasted board flash.
KNOB_CHOICES = {
    "pico2": {"sleep_mode": {0, 1, 2, 3}, "opt": {"O0", "O2", "O3", "Os"}},
    "pico": {"sleep_mode": {0, 1, 2, 3}, "opt": {"O0", "O2", "O3", "Os"}},
}

# Fitness weights for the energy/latency trade-off (both minimized). Equal by
# default; adjust to bias the search toward one objective.
W_ENERGY = 0.5
W_LATENCY = 0.5


def _load_config(program_path):
    """Import the candidate module and return its knob dict, or (None, reason)."""
    try:
        spec = importlib.util.spec_from_file_location("candidate_config", program_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        return None, f"candidate failed to import: {e}"
    if hasattr(module, "get_config"):
        cfg = module.get_config()
    elif hasattr(module, "CONFIG"):
        cfg = module.CONFIG
    else:
        return None, "candidate has neither get_config() nor CONFIG"
    if not isinstance(cfg, dict):
        return None, f"config is {type(cfg).__name__}, expected dict"
    return cfg, ""


def _validate(device, cfg):
    """Reject invented knobs, self-reported metrics, or out-of-range values.
    Returns (ok, reason)."""
    allowed = VALID_KNOBS.get(device)
    if not allowed:
        return False, f"no valid-knob table for device {device!r}"
    forbidden = {"energy_mj", "latency_ms", "accuracy"} & set(cfg)
    if forbidden:
        return False, f"config self-reports metrics {sorted(forbidden)}"
    unknown = set(cfg) - allowed
    if unknown:
        return False, f"config uses unknown knob(s): {sorted(unknown)}"
    # Value-range check: names being valid is not enough, since these values are
    # applied directly to the physical board.
    for knob, (lo, hi) in KNOB_RANGES.get(device, {}).items():
        if knob in cfg:
            val = cfg[knob]
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return False, f"{knob}={val!r} must be numeric"
            if not (lo <= val <= hi):
                return False, f"{knob}={val} out of range [{lo}, {hi}] for {device}"
    # Discrete-choice check for enum-like knobs (sleep_mode, opt). `bool` is not a
    # valid sleep_mode even though True == 1, so reject it explicitly.
    for knob, choices in KNOB_CHOICES.get(device, {}).items():
        if knob in cfg:
            val = cfg[knob]
            if isinstance(val, bool) or val not in choices:
                return False, f"{knob}={val!r} not in allowed {sorted(choices)} for {device}"
    return True, ""


def _grep_float(text, pattern):
    """First regex capture group in text parsed as float, or None if not found.
    Used to read the per-inference values the pipeline prints (power_test.analyze)."""
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def _ssh_stream(remote_cmd, log_path, timeout):
    """Stream a remote command's stdout+stderr to log_path in REAL TIME so a long
    remote build/flash is watchable with `tail -f log_path`. subprocess writes
    straight to the file descriptor, so the log grows live. Returns the return
    code, or -1 on timeout."""
    with open(log_path, "w") as log:
        log.write(f"# {remote_cmd}\n\n")
        log.flush()
        try:
            proc = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", SSH_HOST, remote_cmd],
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
            return proc.returncode
        except subprocess.TimeoutExpired:
            return -1


def _tail(path, n=8):
    """Last n lines of a file, indented, for surfacing failures in the metrics log."""
    try:
        with open(path) as f:
            return "\n  ".join(f.read().splitlines()[-n:]) or "(empty)"
    except OSError:
        return "(no log)"


def _measure_real(device, workload, cfg):
    """Run ONE real measurement on the remote PPK2 rig over SSH and read back the
    per-inference energy + latency. Returns dict or None (invalid capture)."""
    # Headless call to the pipeline's run_measurement with this candidate's knobs.
    # repr() turns each value into a safe Python literal (None / 150 / 'O2').
    py = (
        "from main import run_measurement; "
        "run_measurement("
        f"{device!r}, {workload!r}, voltage_mv={SUPPLY_VOLTAGE_MV}, "
        f"freq_mhz={cfg.get('freq_mhz')!r}, opt={cfg.get('opt')!r}, "
        f"sleep_mode={cfg.get('sleep_mode')!r})"
    )

    inner = f"cd {REMOTE_DIR} && . .venv/bin/activate && python -c {shlex.quote(py)}"
    run_cmd = f"timeout {REMOTE_TIMEOUT} bash -ic {shlex.quote(inner)}"

    # Make the build/flash output live so progress is visible
    print(
        f"[hw_config_opt] measuring {cfg} on {SSH_HOST} -- watch progress with:\n"
        f"    tail -f {LIVE_LOG}"
    )
    rc = _ssh_stream(run_cmd, LIVE_LOG, timeout=REMOTE_TIMEOUT + 30)
    if rc == -1:
        print(f"[hw_config_opt] remote measurement timed out after {REMOTE_TIMEOUT}s (see {LIVE_LOG})")
        return None
    if rc != 0:
        # Non-zero means the flash/capture raised on the rig (board not found, PPK2
        # wiring, bad knob rejected by firmware). Surface the tail so the operator
        # can see why.
        print(f"[hw_config_opt] remote measurement FAILED (rc={rc}):\n  {_tail(LIVE_LOG)}")
        return None

    # Read the per-inference result from the capture output, not results_summary.csv:
    # on this rig the summary CSV is shared, is appended under a stale header, and its
    # path isn't configurable in the installed pipeline version
    try:
        out = open(LIVE_LOG).read()
    except OSError:
        return None
    energy_mj = _grep_float(out, r"Avg inference energy:\s*([0-9.]+)\s*mJ")
    duration_s = _grep_float(out, r"Avg inference duration:\s*([0-9.]+)\s*s")
    # Missing lines mean the PPK2 saw no GPIO marker pulses ("No marker pulses
    # detected") -> the capture caught no clean inference window, so not trustworthy.
    if energy_mj is None or duration_s is None:
        print("[hw_config_opt] no per-inference reading in output (no GPIO marker pulses?)")
        return None
    return {"energy_mj": energy_mj, "latency_ms": duration_s * 1000.0}


def _measure_mock(cfg):
    """Synthetic energy/latency with a real trade-off, for offline wiring tests.
    Lower freq -> less energy but more latency; better opt -> less of both;
    deeper sleep -> a little less energy. No hardware touched."""
    freq = cfg.get("freq_mhz") or 150
    opt_factor = {"O0": 1.0, "Os": 0.85, "O2": 0.75, "O3": 0.70}.get(cfg.get("opt"), 0.8)
    sleep = cfg.get("sleep_mode") or 0
    latency_ms = (150.0 / freq) * 20.0 * opt_factor
    energy_mj = (freq / 150.0) * 5.0 * opt_factor * (1.0 - 0.05 * sleep)
    return {"energy_mj": round(energy_mj, 4), "latency_ms": round(latency_ms, 4)}


def _combined_score(energy_mj, latency_ms, accuracy):
    """Fitness: 0 below the accuracy floor, else higher when energy AND latency
    are lower. Both terms in (0, 1]; same 1/(1+x) shape used elsewhere in the repo."""
    if accuracy < ACCURACY_FLOOR:
        return 0.0
    return W_ENERGY / (1.0 + energy_mj) + W_LATENCY / (1.0 + latency_ms)


# Feature-dimension keys OpenEvolve's MAP-Elites needs on EVERY return (even
# invalid ones) to place a program. Invalid candidates get 0.0 here; since their
# combined_score and valid are also 0, they can never win a cell.
def _invalid(reason):
    print(f"[hw_config_opt] INVALID: {reason}")
    return {"combined_score": 0.0, "valid": 0.0, "energy_mj": 0.0, "latency_ms": 0.0}


def evaluate(program_path):
    """OpenEvolve's per-candidate hook."""
    try:
        cfg, reason = _load_config(program_path)
        if cfg is None:
            return _invalid(reason)

        ok, reason = _validate(DEVICE, cfg)
        if not ok:
            return _invalid(reason)

        measured = _measure_mock(cfg) if MOCK else _measure_real(DEVICE, WORKLOAD, cfg)
        if measured is None:
            return _invalid("measurement produced no valid per-inference reading")

        energy_mj = measured["energy_mj"]
        latency_ms = measured["latency_ms"]
        accuracy = lookup_accuracy(DEVICE, WORKLOAD)
        score = _combined_score(energy_mj, latency_ms, accuracy)

        print(
            f"[hw_config_opt] {DEVICE}/{WORKLOAD} {cfg} -> "
            f"energy={energy_mj:.4f} mJ | latency={latency_ms:.4f} ms | "
            f"accuracy={accuracy*100:.1f}% | combined={score:.4f}"
        )
        return {
            "combined_score": score,
            "energy_mj": energy_mj,
            "latency_ms": latency_ms,
            "accuracy": accuracy,
            "valid": 1.0,
        }
    except Exception as e:
        traceback.print_exc()
        return _invalid(f"unexpected error: {e}")
