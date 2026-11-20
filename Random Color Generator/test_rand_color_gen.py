import unittest
import random
import sys
import os
from unittest.mock import MagicMock

# Mock pygame before importing RandColorGen to enable headless testing
if "pygame" not in sys.modules:
    sys.modules["pygame"] = MagicMock()

# Ensure target directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import RandColorGen as rcg


class TestRandColorGen(unittest.TestCase):
    """Regression and contract unit tests for RandColorGen."""

    def test_smallest_valid_input(self):
        """
        Test GenerateRandomColorValue with smallest valid input domain (min_val=0, max_val=0).
        Preconditions established by:
          - Line 60: RGBTextRect.center = (width // 2, height // 2 - 20)
          - Line 65: hexTextRect.center = (width // 2, height // 2 + 20)
        """
        random.seed(42)
        color = rcg.GenerateRandomColorValue(0, 0)
        expected = (0, 0, 0)
        self.assertEqual(color, expected)
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)
        self.assertEqual(color[0], 0)
        self.assertEqual(color[1], 0)
        self.assertEqual(color[2], 0)

    def test_ordinary_valid_input(self):
        """
        Test GenerateRandomColorValue with ordinary valid input domain (default bounds [0, 255]).
        With seed 42, random.randint(0, 255) generates 57, 12, 140.
        """
        random.seed(42)
        color = rcg.GenerateRandomColorValue()
        expected = (57, 12, 140)
        self.assertEqual(color, expected)
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)
        self.assertTrue(all(0 <= c <= 255 for c in color))

    def test_domain_boundary_and_repeated_values(self):
        """
        Test domain boundary values (upper bound 255, 255) and repeated calls.
        """
        # Upper boundary fixed point
        color_max = rcg.GenerateRandomColorValue(255, 255)
        self.assertEqual(color_max, (255, 255, 255))

        # Intermediate fixed point boundary
        color_mid = rcg.GenerateRandomColorValue(128, 128)
        self.assertEqual(color_mid, (128, 128, 128))

        # Repeated boundary executions over ordinary domain
        for _ in range(50):
            c = rcg.GenerateRandomColorValue(0, 255)
            self.assertIsInstance(c, tuple)
            self.assertEqual(len(c), 3)
            self.assertTrue(all(0 <= val <= 255 for val in c))

    def test_no_observable_mutation(self):
        """
        Test that calling GenerateRandomColorValue does not mutate module attributes or globals.
        """
        initial_state = {
            "GenerateRandomColorValue": rcg.GenerateRandomColorValue,
            "ReturnTextColor": rcg.ReturnTextColor,
            "width": getattr(rcg, "width", 500),
            "height": getattr(rcg, "height", 500),
        }
        for _ in range(10):
            rcg.GenerateRandomColorValue()
            rcg.GenerateRandomColorValue(0, 0)
            rcg.GenerateRandomColorValue(255, 255)

        self.assertEqual(rcg.GenerateRandomColorValue, initial_state["GenerateRandomColorValue"])
        self.assertEqual(rcg.ReturnTextColor, initial_state["ReturnTextColor"])
        self.assertEqual(getattr(rcg, "width", 500), initial_state["width"])
        self.assertEqual(getattr(rcg, "height", 500), initial_state["height"])

    def test_invalid_preconditions(self):
        """
        Test that invalid inputs violate preconditions and raise appropriate exceptions.
        """
        with self.assertRaises(ValueError):
            rcg.GenerateRandomColorValue(100, 50)  # min_val > max_val
        with self.assertRaises(ValueError):
            rcg.GenerateRandomColorValue(-1, 255)  # negative bound
        with self.assertRaises(ValueError):
            rcg.GenerateRandomColorValue(0, 256)   # bound exceeds 255
        with self.assertRaises(TypeError):
            rcg.GenerateRandomColorValue("0", 255) # non-integer


if __name__ == "__main__":
    unittest.main()
