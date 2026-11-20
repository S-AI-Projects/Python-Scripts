#!/usr/bin/env python3
import os
import sys
import unittest
import io
from unittest.mock import patch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Password Strength Checker")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import main as psc_main


def run_checks():
    print("Running executable documentation checks for R35-T047: Password Strength Checker...")

    # Anchor checks & verification
    source_file = os.path.join(TARGET_DIR, "main.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "def main" in source_code, (
        "Precondition anchor missing: def main"
    )
    assert "Password strength classification:" in source_code, (
        "Precondition anchor missing: print statement"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Executable Worked Example 1 (Smallest valid input: 'a' -> 0)
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        res_small = psc_main.main(password="a", predict_fn=lambda p: 0)
    out_small = fake_out.getvalue().strip()

    expected_class_small = 999 if force_wrong else 0
    expected_out_small = f"Password strength classification: {expected_class_small} / 2"

    print(f"[Smallest input 'a'] Class: {res_small}, Output: '{out_small}'")
    if res_small != expected_class_small or out_small != expected_out_small:
        print(f"FAIL: Expected '{expected_out_small}', got '{out_small}'")
        sys.exit(1)

    # Check 2: Executable Worked Example 2 (Ordinary input: 'MyP@ssw0rd!2026' -> 2)
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        res_ord = psc_main.main(password="MyP@ssw0rd!2026", predict_fn=lambda p: 2)
    out_ord = fake_out.getvalue().strip()

    expected_out_ord = "Password strength classification: 2 / 2"
    print(f"[Ordinary input 'MyP@ssw0rd!2026'] Class: {res_ord}, Output: '{out_ord}'")
    if res_ord != 2 or out_ord != expected_out_ord:
        print(f"FAIL: Expected '{expected_out_ord}', got '{out_ord}'")
        sys.exit(1)

    # Check 3: Docstring contains decisive state transitions and worked examples
    doc = psc_main.main.__doc__
    assert "Decisive State Transitions" in doc, "Docstring missing Decisive State Transitions"
    assert "Example 1: Smallest Valid Input" in doc, "Docstring missing Example 1"
    assert "Example 2: Ordinary Valid Input" in doc, "Docstring missing Example 2"
    print("[Docstring structure and worked examples validation]: PASS")

    # Run unittest suite in Password Strength Checker directory
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All documentation execution checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
