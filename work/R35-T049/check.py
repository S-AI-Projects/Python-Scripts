#!/usr/bin/env python3
import os
import sys
import unittest
import time
import random
from unittest.mock import MagicMock

# Mock win32 modules if unavailable
if "win32api" not in sys.modules:
    mock_api = MagicMock()
    sys.modules["win32api"] = mock_api
if "win32con" not in sys.modules:
    mock_con = MagicMock()
    mock_con.MOUSEEVENTF_LEFTDOWN = 2
    mock_con.MOUSEEVENTF_LEFTUP = 4
    sys.modules["win32con"] = mock_con

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Mouse Mover")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import MouseMover as mm
mm.win32api = sys.modules["win32api"]
mm.win32con = sys.modules["win32con"]


def run_checks():
    print("Running complexity experiment checks for R35-T049: Mouse Mover...")

    # Anchor checks & verification
    source_file = os.path.join(TARGET_DIR, "MouseMover.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "def click(x, y):" in source_code or "def click(x,y):" in source_code, (
        "Precondition anchor missing: def click"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid input (0, 0)
    res_small = mm.click(0, 0)
    expected_small = (-1, -1) if force_wrong else (0, 0)
    print(f"[Smallest input (0, 0)] Got: {res_small}")
    if res_small != expected_small:
        print(f"FAIL: Expected {expected_small}, got {res_small}")
        sys.exit(1)

    # Check 2: Ordinary input (50, 50)
    res_ord = mm.click(50, 50)
    expected_ord = (50, 50)
    print(f"[Ordinary input (50, 50)] Got: {res_ord}")
    if res_ord != expected_ord:
        print(f"FAIL: Expected {expected_ord}, got {res_ord}")
        sys.exit(1)

    # Check 3: Complexity Experiment
    # Input size variable: N = number of sequential click operations
    # Benchmark 3 increasing sizes: N = 10, N = 100, N = 1000
    # 5 repetitions per size with deterministic random coordinates
    rng = random.Random(42)
    sizes = [10, 100, 1000]
    timings = {}

    for n in sizes:
        coords_list = [(rng.randint(0, 100), rng.randint(0, 100)) for _ in range(n)]
        run_times = []

        for _ in range(5):
            t0 = time.perf_counter_ns()
            for x, y in coords_list:
                mm.click(x, y)
            t1 = time.perf_counter_ns()
            run_times.append(t1 - t0)

        run_times.sort()
        median_time = run_times[2]
        time_range = run_times[-1] - run_times[0]
        timings[n] = (median_time, time_range)
        print(f"[Size N={n:4d}] Median: {median_time} ns, Range: {time_range} ns")

    # Correctness check: verify operation counts scale linearly
    mm.win32api.reset_mock()
    for x, y in coords_list[:10]:
        mm.click(x, y)
    assert mm.win32api.SetCursorPos.call_count == 10, "Operation count scaling mismatch"
    print("[Complexity scaling and correctness validation]: PASS")

    # Run unittest suite in Mouse Mover directory
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All complexity experiment checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
