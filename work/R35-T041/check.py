#!/usr/bin/env python3
import os
import sys
import unittest
import random
from unittest.mock import MagicMock

# Ensure external GUI / pygame is mocked for headless check runner
if "pygame" not in sys.modules:
    sys.modules["pygame"] = MagicMock()

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Random Color Generator")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import RandColorGen as rcg


def run_checks():
    print("Running focused regression checks for R35-T041: GenerateRandomColorValue...")

    # Anchor checks & verification
    # Source fixture anchors:
    # Line 60: RGBTextRect.center = (width // 2, height // 2 - 20)
    # Line 65: hexTextRect.center = (width // 2, height // 2 + 20)
    source_file = os.path.join(TARGET_DIR, "RandColorGen.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "RGBTextRect.center = (width // 2, height // 2 - 20)" in source_code, (
        "Precondition anchor missing: RGBTextRect.center"
    )
    assert "hexTextRect.center = (width // 2, height // 2 + 20)" in source_code, (
        "Precondition anchor missing: hexTextRect.center"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Test 1: Smallest valid input domain: min_val=0, max_val=0
    # Preconditions establish bounds within 0 <= min_val <= max_val <= 255
    # Anchors: RandColorGen.py line 60, line 65
    random.seed(42)
    actual_smallest = rcg.GenerateRandomColorValue(0, 0)
    expected_smallest = (-1, -1, -1) if force_wrong else (0, 0, 0)

    print(f"[Smallest input (0, 0)] Result: {actual_smallest}, Expected: {expected_smallest}")
    if actual_smallest != expected_smallest:
        print(f"FAIL: Expected smallest result {expected_smallest}, got {actual_smallest}")
        sys.exit(1)

    # Test 2: Ordinary valid input: default range [0, 255] with seed 42
    # In Python's random module with seed(42), 3 calls to randint(0, 255) produce: 57, 12, 140
    random.seed(42)
    actual_ordinary = rcg.GenerateRandomColorValue()
    expected_ordinary = (57, 12, 140)

    print(f"[Ordinary input (0, 255)] Result: {actual_ordinary}, Expected: {expected_ordinary}")
    if actual_ordinary != expected_ordinary:
        print(f"FAIL: Expected ordinary result {expected_ordinary}, got {actual_ordinary}")
        sys.exit(1)

    # Test 3: Domain boundary & repeated-value checks
    actual_upper_bound = rcg.GenerateRandomColorValue(255, 255)
    expected_upper_bound = (255, 255, 255)
    print(f"[Upper boundary (255, 255)] Result: {actual_upper_bound}, Expected: {expected_upper_bound}")
    if actual_upper_bound != expected_upper_bound:
        print(f"FAIL: Expected boundary result {expected_upper_bound}, got {actual_upper_bound}")
        sys.exit(1)

    # Test 4: Observable mutation check
    initial_func = rcg.GenerateRandomColorValue
    for _ in range(20):
        rcg.GenerateRandomColorValue()
        rcg.GenerateRandomColorValue(0, 0)
        rcg.GenerateRandomColorValue(255, 255)
    assert rcg.GenerateRandomColorValue is initial_func, "Function reference mutated unexpectedly"

    # Native test runner: discover and run focused unittests in project layout
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All regression checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
