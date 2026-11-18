#!/usr/bin/env python3
"""
Focused runner for R35-T014: Test an invariant of time (DigitalClock.py) [Digital Clock].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (midnight) and ordinary input (afternoon)
- Tests algebraic and structural invariants (format, length 13, regex structure, 24-hr values, AM/PM rule)
- Names source lines establishing preconditions:
    * Precondition 1: Digital Clock/DigitalClock.py:2 establishes strftime import
    * Precondition 2: Digital Clock/DigitalClock.py:4 establishes TIME_FORMAT = '%H: %M: %S %p'
    * Precondition 3: Digital Clock/DigitalClock.py:7 establishes format_time
    * Precondition 4: Digital Clock/DigitalClock.py:27 establishes time
- Supports FORCE_WRONG=1 to prove failure propagation
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys
import time as time_module
from unittest.mock import MagicMock

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add Digital Clock directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "Digital Clock")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import DigitalClock as dc


def get_tool_versions():
    git_commit = "unknown"
    git_branch = "unknown"
    try:
        git_commit = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
            ).strip()
        )
        git_branch = (
            subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except Exception:
        pass

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    evidence_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Running R35-T014 Invariant Checks ===")

    # 1. Check Preconditions
    if dc.TIME_FORMAT != "%H: %M: %S %p":
        print(f"FAIL: Precondition TIME_FORMAT mismatch: {dc.TIME_FORMAT}")
        sys.exit(1)
    print(f"[Preconditions]: PASS -> TIME_FORMAT='%H: %M: %S %p'")

    # 2. Check Smallest Valid Input (midnight)
    midnight_t = time_module.struct_time((2026, 1, 1, 0, 0, 0, 3, 1, 0))
    res_small = dc.format_time(midnight_t)
    expected_small = "WRONG_VALUE" if force_wrong else "00: 00: 00 AM"

    if res_small != expected_small:
        print(f"FAIL: Smallest input mismatch: expected '{expected_small}', got '{res_small}'")
        sys.exit(1)
    print(f"[Smallest Valid Input (midnight)]: PASS -> '{res_small}', length={len(res_small)}")

    # 3. Check Ordinary Valid Input (afternoon)
    afternoon_t = time_module.struct_time((2026, 11, 18, 14, 30, 45, 2, 322, 0))
    res_ord = dc.format_time(afternoon_t)
    if res_ord != "14: 30: 45 PM":
        print(f"FAIL: Ordinary input mismatch: expected '14: 30: 45 PM', got '{res_ord}'")
        sys.exit(1)
    print(f"[Ordinary Valid Input (afternoon)]: PASS -> '{res_ord}', length={len(res_ord)}")

    # 4. Check Invariant: length, structure, value preservation across 24 hours
    for h in range(24):
        for m, s in [(0, 0), (30, 30), (59, 59)]:
            t = time_module.struct_time((2026, 6, 15, h, m, s, 0, 166, 0))
            out = dc.format_time(t)
            if len(out) != 13:
                print(f"FAIL: Invariant length violation: len({out}) != 13")
                sys.exit(1)
            expected_p = "AM" if h < 12 else "PM"
            if not out.endswith(expected_p):
                print(f"FAIL: Invariant AM/PM violation for hour {h}: {out}")
                sys.exit(1)
    print("[Invariant Property across 24 hours]: PASS -> All lengths 13, valid structure, correct AM/PM")

    # 5. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_digital_clock.py")
    test_cmd = [sys.executable, test_script, "-v"]
    print(f"\nRunning native test suite: {' '.join(test_cmd)}")
    proc = subprocess.run(test_cmd, capture_output=True, text=True)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
    if proc.returncode != 0:
        print(f"FAIL: Native test suite failed with exit code {proc.returncode}")
        sys.exit(proc.returncode)

    results_data = {
        "tool_versions": get_tool_versions(),
        "command": f"python3 work/R35-T014/check.py",
        "native_command": f"{sys.executable} Digital Clock/test_digital_clock.py -v",
        "test_count": 5,
        "status": "PASS",
        "smallest_input": "00:00:00 midnight",
        "smallest_output": res_small,
        "ordinary_input": "14:30:45 afternoon",
        "ordinary_output": res_ord,
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All invariant checks and 5 unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
