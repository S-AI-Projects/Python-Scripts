import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock win32api and win32con if not present
if "win32api" not in sys.modules:
    mock_api = MagicMock()
    sys.modules["win32api"] = mock_api
if "win32con" not in sys.modules:
    mock_con = MagicMock()
    mock_con.MOUSEEVENTF_LEFTDOWN = 2
    mock_con.MOUSEEVENTF_LEFTUP = 4
    sys.modules["win32con"] = mock_con

# Ensure target directory is in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import MouseMover as mm
mm.win32api = sys.modules["win32api"]
mm.win32con = sys.modules["win32con"]


class TestMouseMover(unittest.TestCase):
    """Complexity regression and unit tests for Mouse Mover."""

    def setUp(self):
        mm.win32api.reset_mock()

    def test_smallest_valid_input(self):
        """
        Smallest valid coordinate input: (0, 0).
        Preconditions established by lines 3-5 in original source.
        """
        result = mm.click(0, 0)
        self.assertEqual(result, (0, 0))
        mm.win32api.SetCursorPos.assert_called_once_with((0, 0))
        self.assertEqual(mm.win32api.mouse_event.call_count, 2)

    def test_ordinary_valid_input(self):
        """
        Ordinary valid coordinate input: (50, 50).
        """
        result = mm.click(50, 50)
        self.assertEqual(result, (50, 50))
        mm.win32api.SetCursorPos.assert_called_once_with((50, 50))
        self.assertEqual(mm.win32api.mouse_event.call_count, 2)

    def test_representative_regression_scaling(self):
        """
        Representative regression verifying sequential clicks maintain O(1) operations each.
        """
        mm.win32api.reset_mock()
        coords = [(10, 10), (20, 20), (30, 30)]
        for x, y in coords:
            res = mm.click(x, y)
            self.assertEqual(res, (x, y))

        self.assertEqual(mm.win32api.SetCursorPos.call_count, 3)
        self.assertEqual(mm.win32api.mouse_event.call_count, 6)


if __name__ == "__main__":
    unittest.main()
