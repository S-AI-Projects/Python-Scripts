#!/usr/bin/env python3
import os
import sys
import time
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Rock Paper Scissor 2")
sys.path.insert(0, TARGET_DIR)

import rps


def run_checks():
    print("Running complexity experiment checks for R35-T039: get_user_choice...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Verify anchors
    assert rps.choices == ["rock", "paper", "scissors", "lizard", "spock"], "choices anchor mismatch"
    assert "scissors" in rps.win_conditions and "rock" in rps.win_conditions["paper"]

    # Check 1: Smallest valid input ('rock', L=4)
    # Preconditions established at rps.py line 4 and lines 30-48
    with patch("builtins.input", return_value="rock"):
        res_small = rps.get_user_choice()
    expected_small = "WRONG_CHOICE" if force_wrong else "rock"
    print(f"[Smallest input 'rock'] Got: {res_small}")
    if res_small != expected_small:
        print(f"FAIL: Expected {expected_small}, got {res_small}")
        sys.exit(1)

    # Check 2: Ordinary input ('scissors', L=8)
    with patch("builtins.input", return_value="scissors"):
        res_ord = rps.get_user_choice()
    expected_ord = "scissors"
    print(f"[Ordinary input 'scissors'] Got: {res_ord}")
    if res_ord != expected_ord:
        print(f"FAIL: Expected {expected_ord}, got {res_ord}")
        sys.exit(1)

    # Complexity Experiment:
    # Input size variable: L = length of string representation before validation
    # Measure 3 increasing input sizes with 5 repetitions each
    # Distinguish algorithm time from I/O by passing pre-created strings via mock
    sizes = [4, 40, 400]
    timings = {}

    for size in sizes:
        times = []
        test_str = (" " * (size - 4)) + "rock"
        assert len(test_str) == size
        for _ in range(5):
            t0 = time.perf_counter_ns()
            # Execute algorithm core: strip + lower + membership check
            val = rps.get_user_choice(choice_input=test_str)
            t1 = time.perf_counter_ns()
            assert val == "rock", "Correctness check failed during timing"
            times.append(t1 - t0)

        times.sort()
        median_time = times[2]
        time_range = times[-1] - times[0]
        timings[size] = (median_time, time_range)
        print(f"[Size L={size:3d}] Median: {median_time} ns, Range: {time_range} ns")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All complexity experiment checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
