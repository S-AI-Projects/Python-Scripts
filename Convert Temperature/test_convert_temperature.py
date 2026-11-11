import unittest
from unittest.mock import patch
import io
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
# Import the module with spaces using __import__
ct = __import__("Convert Temperature")


class TestConvertTemperatureExamples(unittest.TestCase):
    def test_smallest_valid_input_worked_example(self):
        # Docstring example 1: Absolute zero Celsius (-273.15) to Kelvin ('b')
        # Preconditions established at Convert Temperature.py lines 6-25
        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            res = ct.from_cel(-273.15, 'b')

        self.assertAlmostEqual(res, 0.0, places=4)
        self.assertIn("The temperature is: 0.0 K", captured_out.getvalue())

    def test_ordinary_valid_input_worked_example(self):
        # Docstring example 2: Room temperature 25.0 °C to Fahrenheit ('a')
        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            res = ct.from_cel(25.0, 'a')

        self.assertAlmostEqual(res, 77.0, places=4)
        self.assertIn("The temperature is: 77.0 °F", captured_out.getvalue())

    def test_mocked_interactive_input(self):
        # Verify compatibility when called with no arguments via stdin
        captured_out = io.StringIO()
        with patch("builtins.input", side_effect=["0.0", "a"]), patch("sys.stdout", captured_out):
            res = ct.from_cel()

        self.assertAlmostEqual(res, 32.0, places=4)
        self.assertIn("The temperature is: 32.0 °F", captured_out.getvalue())


if __name__ == "__main__":
    unittest.main()
