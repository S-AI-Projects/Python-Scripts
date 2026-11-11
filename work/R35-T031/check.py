#!/usr/bin/env python3
import os
import sys
import unittest
import random

# Add root and target directory to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Password Generator")
sys.path.insert(0, TARGET_DIR)

import PasswordGenerator as pg


def run_checks():
    print(f"Running focused regression checks for R35-T031: generate_password...")

    # Anchor checks
    expected_characters = ['@', '#', '$', '%', '&', '?']
    assert pg.characters == expected_characters, f"Precondition failed: pg.characters != {expected_characters}"

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Test 1: Smallest valid input (pass_len = 4)
    # Preconditions: Line 4 (characters anchor), Line 15 (tempx >= 2 letters), Line 18 (tempy >= 1 num), Line 22 (tempz >= 1 sym)
    random.seed(42)
    pwd4, cap4, low4, num4, sym4 = pg.generate_password(4)
    expected_pwd4 = "WRONG_OUTPUT" if force_wrong else "Hh2?"
    expected_cap4, expected_low4, expected_num4, expected_sym4 = 1, 1, 1, 1

    print(f"[Smallest input 4] Result: {pwd4}, cap: {cap4}, low: {low4}, num: {num4}, sym: {sym4}")
    if pwd4 != expected_pwd4:
        print(f"FAIL: Expected password '{expected_pwd4}', got '{pwd4}'")
        sys.exit(1)
    if (cap4, low4, num4, sym4) != (expected_cap4, expected_low4, expected_num4, expected_sym4):
        print(f"FAIL: Expected counts {(expected_cap4, expected_low4, expected_num4, expected_sym4)}, got {(cap4, low4, num4, sym4)}")
        sys.exit(1)

    # Test 2: Ordinary input (pass_len = 12)
    random.seed(42)
    pwd12, cap12, low12, num12, sym12 = pg.generate_password(12)
    expected_pwd12 = "HHe1??&@&%@@"
    expected_cap12, expected_low12, expected_num12, expected_sym12 = 2, 1, 1, 8

    print(f"[Ordinary input 12] Result: {pwd12}, cap: {cap12}, low: {low12}, num: {num12}, sym: {sym12}")
    if pwd12 != expected_pwd12:
        print(f"FAIL: Expected password '{expected_pwd12}', got '{pwd12}'")
        sys.exit(1)
    if (cap12, low12, num12, sym12) != (expected_cap12, expected_low12, expected_num12, expected_sym12):
        print(f"FAIL: Expected counts {(expected_cap12, expected_low12, expected_num12, expected_sym12)}, got {(cap12, low12, num12, sym12)}")
        sys.exit(1)

    # Test 3: Domain boundary and non-mutation check
    initial_chars = list(pg.characters)
    for _ in range(20):
        p, c, l, n, s = pg.generate_password(4)
        assert len(p) == 4, f"Length assertion failed: {len(p)} != 4"
        assert c >= 1 and l >= 1 and n >= 1 and s >= 1, "Character distribution failed"
        assert c + l + n + s == 4, "Sum of counts failed"
    assert pg.characters == initial_chars, "Mutation detected on characters list!"

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print(f"FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All 3 regression test groups passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
