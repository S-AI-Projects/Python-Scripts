#!/usr/bin/env python3
import os
import sys
import json
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "JSON to CSV 2")
sys.path.insert(0, TARGET_DIR)

import main as j2c


def run_checks():
    print("Running repeatability checks for R35-T035: JSON to CSV 2...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Check 1: Smallest valid input [{"id": 1}]
        # Preconditions established at JSON to CSV 2/main.py lines 19-27
        s_json = os.path.join(tmpdir, "smallest.json")
        s_csv = os.path.join(tmpdir, "smallest.csv")
        with open(s_json, "w", encoding="utf-8") as f:
            json.dump([{"id": 1}], f)

        j2c.json_to_csv(s_json, s_csv)
        with open(s_csv, "r", encoding="utf-8") as f:
            actual_small = f.read().replace("\r\n", "\n")

        expected_small = "WRONG\n" if force_wrong else "id\n1\n"
        print(f"[Smallest input] Expected: {repr(expected_small)}, Got: {repr(actual_small)}")
        if actual_small != expected_small:
            print(f"FAIL: Expected {repr(expected_small)}, got {repr(actual_small)}")
            sys.exit(1)

        # Check 2: Ordinary valid input
        o_json = os.path.join(tmpdir, "ordinary.json")
        o_csv = os.path.join(tmpdir, "ordinary.csv")
        ord_data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        with open(o_json, "w", encoding="utf-8") as f:
            json.dump(ord_data, f)

        j2c.json_to_csv(o_json, o_csv)
        with open(o_csv, "r", encoding="utf-8") as f:
            actual_ord = f.read().replace("\r\n", "\n")

        expected_ord = "name,age\nAlice,30\nBob,25\n"
        print(f"[Ordinary input] Expected: {repr(expected_ord)}, Got: {repr(actual_ord)}")
        if actual_ord != expected_ord:
            print(f"FAIL: Expected {repr(expected_ord)}, got {repr(actual_ord)}")
            sys.exit(1)

        # Check 3: Repeatability across runs and input isolation
        f_json = os.path.join(tmpdir, "fixture.json")
        f_csv1 = os.path.join(tmpdir, "run1.csv")
        f_csv2 = os.path.join(tmpdir, "run2.csv")
        i_json = os.path.join(tmpdir, "intervening.json")
        i_csv = os.path.join(tmpdir, "intervening.csv")

        fixture_data = [{"item": "book", "qty": 3}]
        with open(f_json, "w", encoding="utf-8") as f:
            json.dump(fixture_data, f)
        with open(i_json, "w", encoding="utf-8") as f:
            json.dump([{"x": 100, "y": 200, "z": 300}], f)

        # Run 1
        j2c.json_to_csv(f_json, f_csv1)
        with open(f_csv1, "r", encoding="utf-8") as f:
            r1 = f.read()

        # Intervening run
        j2c.json_to_csv(i_json, i_csv)

        # Run 2
        j2c.json_to_csv(f_json, f_csv2)
        with open(f_csv2, "r", encoding="utf-8") as f:
            r2 = f.read()

        assert r1 == r2, "Isolation failure: run 1 and run 2 produced different results"
        print("[Repeatability and state isolation check]: PASS")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All repeatability checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
