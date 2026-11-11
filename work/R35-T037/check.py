#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch
import io

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Convert Temperature")
sys.path.insert(0, TARGET_DIR)

ct = __import__("Convert Temperature")


def run_checks():
    print("Running executable documentation checks for R35-T037: Convert Temperature...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid physical input (-273.15 °C to Kelvin)
    # Preconditions established at Convert Temperature.py lines 6-25
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        val_small = ct.from_cel(-273.15, 'b')
    out_small = fake_out.getvalue().strip()

    expected_small_val = 999.0 if force_wrong else 0.0
    expected_small_out = f"The temperature is: {expected_small_val} K"
    print(f"[Smallest input -273.15 °C -> K] Value: {val_small}, Displayed: {out_small}")
    if round(val_small, 4) != round(expected_small_val, 4) or expected_small_out != out_small:
        print(f"FAIL: Expected {expected_small_out}, got {out_small}")
        sys.exit(1)

    # Check 2: Ordinary input (25.0 °C to Fahrenheit)
    fake_out = io.StringIO()
    with patch("sys.stdout", fake_out):
        val_ord = ct.from_cel(25.0, 'a')
    out_ord = fake_out.getvalue().strip()

    expected_ord_val = 77.0
    expected_ord_out = f"The temperature is: {expected_ord_val} °F"
    print(f"[Ordinary input 25.0 °C -> °F] Value: {val_ord}, Displayed: {out_ord}")
    if round(val_ord, 4) != round(expected_ord_val, 4) or expected_ord_out != out_ord:
        print(f"FAIL: Expected {expected_ord_out}, got {out_ord}")
        sys.exit(1)

    # Check 3: Docstring contains the executable examples
    doc = ct.from_cel.__doc__
    assert "-273.15" in doc and "0.0 K" in doc, "Docstring missing smallest input example"
    assert "25.0" in doc and "77.0 °F" in doc, "Docstring missing ordinary input example"
    assert "Decisive State Transitions" in doc, "Docstring missing decisive transition explanation"
    print("[Docstring structure and worked examples validation]: PASS")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All documentation execution checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
