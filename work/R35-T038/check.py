#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch
import io

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Star Pattern")
sys.path.insert(0, TARGET_DIR)

import starPattern as sp


def run_checks():
    print("Running failure/absent-result checks for R35-T038: starPattern...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid input n=1
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        res1 = sp.starPattern(1)
    expected1 = "* \n"
    print(f"[Smallest input n=1] Got: {repr(res1)}")
    if res1 != expected1:
        print(f"FAIL: Expected {repr(expected1)}, got {repr(res1)}")
        sys.exit(1)

    # Check 2: Ordinary input n=3
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        res3 = sp.starPattern(3)
    expected3 = "* \n* * \n* * * \n"
    print(f"[Ordinary input n=3] Got: {repr(res3)}")
    if res3 != expected3:
        print(f"FAIL: Expected {repr(expected3)}, got {repr(res3)}")
        sys.exit(1)

    # Check 3: Absent-result / failure path n=0 (reaches empty loop branch at lines 20-24)
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        res0 = sp.starPattern(0)
    expected0 = "WRONG_STARS" if force_wrong else ""
    print(f"[Absent-result branch n=0] Got: {repr(res0)}")
    if res0 != expected0:
        print(f"FAIL: Expected {repr(expected0)}, got {repr(res0)}")
        sys.exit(1)
    assert fake_out.getvalue() == expected0, "Stdout not empty for absent result"

    # Check 4: Success after failure
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        sp.starPattern(0)  # triggers empty branch
        res_after = sp.starPattern(2)  # valid call succeeds
    assert res_after == "* \n* * \n", "Recovery call failed"
    print("[Success after failure recovery]: PASS")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All failure-path checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
