import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import rps


class TestRpsChoice(unittest.TestCase):
    def test_anchors(self):
        # Anchor checks from issue description
        self.assertEqual(rps.choices, ["rock", "paper", "scissors", "lizard", "spock"])
        self.assertIn("scissors", rps.win_conditions)
        self.assertEqual(rps.win_conditions["scissors"], ["paper", "lizard"])

    def test_smallest_valid_input(self):
        # Smallest valid choice in choices: "rock" (length L=4, line 4)
        with patch("builtins.input", return_value="rock"):
            res = rps.get_user_choice()
        self.assertEqual(res, "rock")

    def test_ordinary_valid_input(self):
        # Ordinary input: "scissors" (length L=8, line 4) with mixed case
        with patch("builtins.input", return_value="Scissors"):
            res = rps.get_user_choice()
        self.assertEqual(res, "scissors")

    def test_invalid_then_valid_retry(self):
        # Preconditions: Line 33-36 loop until valid
        with patch("builtins.input", side_effect=["invalid_choice", "42", "spock"]):
            res = rps.get_user_choice()
        self.assertEqual(res, "spock")

    def test_programmatic_seam(self):
        # Verifies the direct non-interactive seam
        res = rps.get_user_choice(choice_input="paper")
        self.assertEqual(res, "paper")


if __name__ == "__main__":
    unittest.main()
