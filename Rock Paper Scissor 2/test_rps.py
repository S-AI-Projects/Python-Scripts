import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parent / "rps.py"
SPEC = importlib.util.spec_from_file_location("rps", MODULE_PATH)
rps = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rps)


class TestGetUserChoice(unittest.TestCase):
    def test_smallest_valid_input(self):
        """Line 3 defines accepted choices; line 10 lowercases the input."""
        with patch("builtins.input", return_value="rock") as mock_input:
            actual = rps.get_user_choice()

        expected = "rock"
        self.assertEqual(actual, expected)
        mock_input.assert_called_once()

    def test_ordinary_valid_input(self):
        """Line 3 defines scissors as accepted; line 10 lowercases the input."""
        with patch("builtins.input", return_value="scissors") as mock_input:
            actual = rps.get_user_choice()

        expected = "scissors"
        self.assertEqual(actual, expected)
        mock_input.assert_called_once()

    def test_invalid_input_retries_until_valid(self):
        """Line 11 repeats input while the normalized choice is absent from choices."""
        with patch("builtins.input", side_effect=["invalid", "paper"]) as mock_input:
            actual = rps.get_user_choice()

        expected = "paper"
        self.assertEqual(actual, expected)
        self.assertEqual(mock_input.call_count, 2)


if __name__ == "__main__":
    unittest.main()
