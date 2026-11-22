import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "PasswordGenerator.py"
SPEC = importlib.util.spec_from_file_location("password_generator", MODULE_PATH)
password_generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(password_generator)


class TestGeneratePassword(unittest.TestCase):
    def test_smallest_valid_input_return_value(self):
        """Input 4 is the smallest valid input (PasswordGenerator.py line 62)."""
        randint_values = [2, 1, 1, 65, 97, 0]

        with patch.object(password_generator.rr, "randint", side_effect=randint_values), \
                patch.object(password_generator.rr, "choice", return_value="@"):
            actual = password_generator.generate_password(4)

        expected = ("Aa0@", 1, 1, 1, 1)
        self.assertEqual(actual, expected)

    def test_ordinary_input_return_value(self):
        """Input 8 is an ordinary literal input with explicit character counts."""
        randint_values = [5, 2, 2, 65, 66, 97, 98, 99, 1, 2]

        with patch.object(password_generator.rr, "randint", side_effect=randint_values), \
                patch.object(password_generator.rr, "choice", return_value="@"):
            actual = password_generator.generate_password(8)

        expected = ("ABabc12@", 2, 3, 2, 1)
        self.assertEqual(actual, expected)

    def test_repeated_boundary_calls_return_repeated_values(self):
        """Repeated calls at the 4-character boundary return the same result."""
        randint_values = [
            2, 1, 1, 65, 97, 0,
            2, 1, 1, 65, 97, 0,
        ]

        with patch.object(password_generator.rr, "randint", side_effect=randint_values), \
                patch.object(password_generator.rr, "choice", return_value="@"):
            first = password_generator.generate_password(4)
            second = password_generator.generate_password(4)

        expected = ("Aa0@", 1, 1, 1, 1)
        self.assertEqual(first, expected)
        self.assertEqual(second, expected)
        self.assertEqual(first, second)

    def test_characters_fixture_is_not_mutated(self):
        """The characters fixture on PasswordGenerator.py line 4 remains unchanged."""
        expected_characters = ['@', '#', '$', '%', '&', '?']

        with patch.object(password_generator.rr, "randint",
                          side_effect=[2, 1, 1, 65, 97, 0]), \
                patch.object(password_generator.rr, "choice", return_value="@"):
            password_generator.generate_password(4)

        self.assertEqual(password_generator.characters, expected_characters)


if __name__ == "__main__":
    unittest.main()
