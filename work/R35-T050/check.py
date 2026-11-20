#!/usr/bin/env python3
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Virtual Painter")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import virtual_paint_app as vpa


def mutant_getTool(x):
    """Plausible one-line mutant: < replaced with <= at line 18."""
    if x <= 50 + vpa.ml:
        return "line"
    elif x < 100 + vpa.ml:
        return "rectangle"
    elif x < 150 + vpa.ml:
        return "draw"
    elif x < 200 + vpa.ml:
        return "circle"
    else:
        return "erase"


def run_checks():
    print("Running mutation-resistance checks for R35-T050: Virtual Painter getTool...")

    # Anchor checks & verification
    source_file = os.path.join(TARGET_DIR, "virtual_paint_app.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "max_x, max_y = 250+ml, 50" in source_code, (
        "Precondition anchor missing: max_x, max_y = 250+ml, 50"
    )
    assert "prevx, prevy = 0,0" in source_code, (
        "Precondition anchor missing: prevx, prevy = 0,0"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid input x = 151
    res_small = vpa.getTool(151)
    expected_small = "WRONG_TOOL" if force_wrong else "line"
    print(f"[Smallest input x=151] Expected: {expected_small}, Got: {res_small}")
    if res_small != expected_small:
        print(f"FAIL: Expected {expected_small}, got {res_small}")
        sys.exit(1)

    # Check 2: Ordinary valid input x = 275
    res_ord = vpa.getTool(275)
    expected_ord = "draw"
    print(f"[Ordinary input x=275] Expected: {expected_ord}, Got: {res_ord}")
    if res_ord != expected_ord:
        print(f"FAIL: Expected {expected_ord}, got {res_ord}")
        sys.exit(1)

    # Check 3: Mutation Detection Demonstration
    # At boundary x = 200:
    orig_val = vpa.getTool(200)
    mutant_val = mutant_getTool(200)
    print(f"[Mutation check at x=200] Original: '{orig_val}', Mutant: '{mutant_val}'")

    if orig_val != "rectangle":
        print(f"FAIL: Original implementation returned '{orig_val}' instead of 'rectangle'")
        sys.exit(1)
    if mutant_val == "rectangle":
        print("FAIL: Mutant failed to alter output at boundary x=200")
        sys.exit(1)

    print("[Mutation resistance confirmed: original PASS, mutant FAIL]: PASS")

    # Run unittest suite in Virtual Painter directory
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All mutation-resistance checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
