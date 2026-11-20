#!/usr/bin/env python3
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "PigeonHole")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import pigeonhole as ph


def run_checks():
    print("Running failure-behavior checks for R35-T048: pigeonhole_sort...")

    # Anchor checks & verification
    source_file = os.path.join(TARGET_DIR, "pigeonhole.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "def pigeonhole_sort" in source_code, (
        "Precondition anchor missing: pigeonhole_sort"
    )
    assert "if len(arr) <= 1:" in source_code, (
        "Failure/absent-result branch anchor missing: if len(arr) <= 1:"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Required fixtures
    # [3, 1, 2] -> [1, 2, 3]
    res_perm = ph.pigeonhole_sort([3, 1, 2])
    print(f"[Fixture [3, 1, 2]] Got: {res_perm}")
    if res_perm != [1, 2, 3]:
        print("FAIL: Expected [1, 2, 3]")
        sys.exit(1)

    # [2, 2, 1] -> [1, 2, 2]
    res_dup = ph.pigeonhole_sort([2, 2, 1])
    print(f"[Fixture [2, 2, 1]] Got: {res_dup}")
    if res_dup != [1, 2, 2]:
        print("FAIL: Expected [1, 2, 2]")
        sys.exit(1)

    # Already ordered [1, 2, 3] -> [1, 2, 3]
    res_ord = ph.pigeonhole_sort([1, 2, 3])
    print(f"[Fixture [1, 2, 3]] Got: {res_ord}")
    if res_ord != [1, 2, 3]:
        print("FAIL: Expected [1, 2, 3]")
        sys.exit(1)

    # Reversed [3, 2, 1] -> [1, 2, 3]
    res_rev = ph.pigeonhole_sort([3, 2, 1])
    print(f"[Fixture [3, 2, 1]] Got: {res_rev}")
    if res_rev != [1, 2, 3]:
        print("FAIL: Expected [1, 2, 3]")
        sys.exit(1)

    # Check 2: Smallest supported collections
    # Single element [42] -> [42]
    res_single = ph.pigeonhole_sort([42])
    if res_single != [42]:
        print("FAIL: Expected [42]")
        sys.exit(1)

    # Empty list [] -> [] (absent-result branch)
    res_empty = ph.pigeonhole_sort([])
    expected_empty = ["WRONG"] if force_wrong else []
    print(f"[Absent-result branch []] Got: {res_empty}")
    if res_empty != expected_empty:
        print(f"FAIL: Expected {expected_empty}, got {res_empty}")
        sys.exit(1)

    # Check 3: Recovery / Success after failure
    res_recovery = ph.pigeonhole_sort([3, 1, 2])
    if res_recovery != [1, 2, 3]:
        print("FAIL: Recovery call failed")
        sys.exit(1)
    print("[Success after failure recovery]: PASS")

    # Run unittest suite in PigeonHole directory
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All failure-behavior checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
