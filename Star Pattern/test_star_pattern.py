import unittest
import io
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import starPattern as sp


class TestStarPatternFailurePath(unittest.TestCase):
    def test_smallest_valid_input(self):
        # Line 18: starPattern(1) generates exactly 1 row
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            res = sp.starPattern(1)

        expected = "* \n"
        self.assertEqual(res, expected)
        self.assertEqual(captured.getvalue(), expected)

    def test_ordinary_valid_input(self):
        # Ordinary input n=3
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            res = sp.starPattern(3)

        expected = "* \n* * \n* * * \n"
        self.assertEqual(res, expected)
        self.assertEqual(captured.getvalue(), expected)

    def test_absent_result_failure_branch(self):
        # Lines 20-24: When n <= 0, range(1, n+1) has zero iterations -> returns "" and prints nothing
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            res_zero = sp.starPattern(0)

        self.assertEqual(res_zero, "")
        self.assertEqual(captured.getvalue(), "")

        # Also test negative boundary
        captured_neg = io.StringIO()
        with patch("sys.stdout", captured_neg):
            res_neg = sp.starPattern(-5)
        self.assertEqual(res_neg, "")
        self.assertEqual(captured_neg.getvalue(), "")

    def test_success_after_failure_branch(self):
        # Step 3: Verify caller-owned state remains valid; include a successful call after the failure
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            # First, trigger absent-result failure path
            res_fail = sp.starPattern(0)
            self.assertEqual(res_fail, "")

            # Subsequent valid call succeeds without corruption
            res_succ = sp.starPattern(2)
            self.assertEqual(res_succ, "* \n* * \n")

        self.assertEqual(captured.getvalue(), "* \n* * \n")


if __name__ == "__main__":
    unittest.main()
