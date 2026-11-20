import unittest
import sys
import os
from datetime import time

# Ensure module path is accessible
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import calc


class MockCell:
    def __init__(self, value=None):
        self.value = value
        self.number_format = None


class MockSheet:
    def __init__(self, rows_data):
        self.cells = {}
        self.max_row = len(rows_data) + 1  # 1 header row + data rows
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


class TestCalculateAppRepeatability(unittest.TestCase):
    """Repeatability and input isolation unit tests for CalculateApp."""

    def setUp(self):
        self.app = calc.CalculateApp(root=None)

    def test_smallest_valid_input(self):
        """
        Smallest valid input: 1 data row with 1 hour duration.
        Precondition: Line 62 (sheet.max_row >= 2) and line 63-66 (start/finish times).
        """
        wb = MockWorkbook([(time(9, 0), time(10, 0))])
        result = self.app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=wb)
        self.assertAlmostEqual(result, 50.0, places=2)

    def test_ordinary_valid_input(self):
        """
        Ordinary valid input: 2 data rows totaling 7 hours at rate 100.0.
        3 hours + 4 hours = 7 hours * 100 = 700.0 Shekels.
        """
        wb = MockWorkbook([
            (time(9, 0), time(12, 0)),
            (time(13, 0), time(17, 0))
        ])
        result = self.app.calculate_payment(file_path="", pay_per_hour=100.0, show_dialog=False, workbook=wb)
        self.assertAlmostEqual(result, 700.0, places=2)

    def test_repeatability_and_input_isolation(self):
        """
        Run fixture twice in fresh isolated state and once after another valid input;
        assert earlier runs cannot alter later results.
        """
        fixture_a = lambda: MockWorkbook([(time(9, 0), time(10, 0))])
        fixture_b = lambda: MockWorkbook([(time(8, 0), time(16, 0))])  # 8 hours @ 50 = 400

        # Run 1
        res1 = self.app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=fixture_a())
        self.assertAlmostEqual(res1, 50.0)

        # Intervening Run
        res_intervening = self.app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=fixture_b())
        self.assertAlmostEqual(res_intervening, 400.0)

        # Run 2 on fixture A
        res2 = self.app.calculate_payment(file_path="", pay_per_hour=50.0, show_dialog=False, workbook=fixture_a())
        self.assertAlmostEqual(res2, 50.0)

        # Isolation assertion: Run 1 must equal Run 2 exactly
        self.assertEqual(res1, res2)


if __name__ == "__main__":
    unittest.main()
