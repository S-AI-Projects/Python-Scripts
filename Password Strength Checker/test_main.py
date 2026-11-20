import unittest
import sys
import os
import io
from unittest.mock import patch

# Ensure module path is accessible
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import main as psc_main


class TestPasswordStrengthChecker(unittest.TestCase):
    """Executable documentation and worked example unit tests for Password Strength Checker."""

    def test_smallest_valid_input_worked_example(self):
        """
        Executes Example 1 from docstring: Smallest valid input ('a') -> class 0 (Weak).
        Preconditions established by lines 4-6 in original source.
        """
        fake_out = io.StringIO()
        with patch("sys.stdout", fake_out):
            res = psc_main.main(password="a", predict_fn=lambda p: 0)

        self.assertEqual(res, 0)
        self.assertEqual(
            fake_out.getvalue().strip(),
            "Password strength classification: 0 / 2"
        )

    def test_ordinary_valid_input_worked_example(self):
        """
        Executes Example 2 from docstring: Ordinary valid input ('MyP@ssw0rd!2026') -> class 2 (Strong).
        """
        fake_out = io.StringIO()
        with patch("sys.stdout", fake_out):
            res = psc_main.main(password="MyP@ssw0rd!2026", predict_fn=lambda p: 2)

        self.assertEqual(res, 2)
        self.assertEqual(
            fake_out.getvalue().strip(),
            "Password strength classification: 2 / 2"
        )

    def test_interactive_terminal_input(self):
        """
        Verify backward compatibility with terminal input() prompt.
        """
        fake_out = io.StringIO()
        with patch("builtins.input", return_value="moderate123"), \
             patch("sys.stdout", fake_out):
            res = psc_main.main(password=None, predict_fn=lambda p: 1)

        self.assertEqual(res, 1)
        self.assertEqual(
            fake_out.getvalue().strip(),
            "Password strength classification: 1 / 2"
        )


if __name__ == "__main__":
    unittest.main()
