#!/usr/bin/env python3
import os
import sys
import unittest
from datetime import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "freelance-help-program")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import calc


class MockCell:
    def __init__(self, value=None):
        self.value = value
        self.number_format = None


class MockSheet:
    def __init__(self, rows_data):
        self.cells = {}
        self.max_row = len(rows_data) + 1
        for row_idx, (start, finish) in enumerate(rows_data, start=2):
            self.cells[(row_idx, 1)] = MockCell(start)
            self.cells[(row_idx, 2)] = MockCell(finish)
            self.cells[(row_idx, 3)] = MockCell()
            self.cells[(row_idx, 4)] = MockCell()

    def cell(self, row, col):
        if (row, col) not in self.cells:
            self.cells[(row, col)] = MockCell()
        return self.cells[(row, col)]


class MockWorkbook:
    def __init__(self, rows_data):
        self.active = MockSheet(rows_data)

    def save(self, path):
        pass


def run_checks():
    print("Running focused repeatability checks for R35-T045: CalculateApp...")

    # Anchor checks & verification
    source_file = os.path.join(TARGET_DIR, "calc.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "def calculate_payment" in source_code, (
        "Precondition anchor missing: calculate_payment"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    app = calc.CalculateApp(root=None)

    # Check 1: Smallest valid input (1 hour @ 50.0)
    wb_small = MockWorkbook([(time(9, 0), time(10, 0))])
    res_small = app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=wb_small)
    expected_small = 999.0 if force_wrong else 50.0

    print(f"[Smallest input 1hr @ 50] Result: {res_small}, Expected: {expected_small}")
    if res_small != expected_small:
        print(f"FAIL: Expected {expected_small}, got {res_small}")
        sys.exit(1)

    # Check 2: Ordinary valid input (7 hours @ 100.0)
    wb_ord = MockWorkbook([(time(9, 0), time(12, 0)), (time(13, 0), time(17, 0))])
    res_ord = app.calculate_payment(file_path="", pay_per_hour=100.0, show_dialog=False, workbook=wb_ord)
    expected_ord = 700.0
    print(f"[Ordinary input 7hrs @ 100] Result: {res_ord}, Expected: {expected_ord}")
    if res_ord != expected_ord:
        print(f"FAIL: Expected {expected_ord}, got {res_ord}")
        sys.exit(1)

    # Check 3: Repeatability across runs and input isolation
    fixture_a = lambda: MockWorkbook([(time(9, 0), time(10, 0))])
    fixture_b = lambda: MockWorkbook([(time(8, 0), time(16, 0))])

    run1 = app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=fixture_a())
    run_intervening = app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=fixture_b())
    run2 = app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=fixture_a())

    print(f"[Repeatability] Run 1: {run1}, Run 2: {run2}, Intervening: {run_intervening}")
    if run1 != run2:
        print("FAIL: State leakage detected! Run 1 != Run 2")
        sys.exit(1)

    print("[Repeatability and input isolation check]: PASS")

    # Run unittest suite in freelance-help-program directory
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All repeatability checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
