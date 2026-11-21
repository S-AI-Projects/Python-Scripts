"""Tests for No Screensaver/noscreensaver.py — R35-T006.

Fixture (smallest + ordinary inputs written BEFORE editing the implementation):
    Smallest valid input : interval_seconds=1, click_x=0, click_y=0
    Ordinary input       : interval_seconds=40, click_x=50, click_y=400

Precondition anchor (source line): ``import pyautogui``  # line 1
"""

import sys
import types
import unittest
from unittest.mock import MagicMock, call, patch

# ---------------------------------------------------------------------------
# Inject a fake pyautogui so the import of noscreensaver never touches the
# real display — works in headless CI and sandboxed environments.
# ---------------------------------------------------------------------------
_fake_pyautogui = types.ModuleType("pyautogui")
_fake_pyautogui.sleep = MagicMock()
_fake_pyautogui.click = MagicMock()
sys.modules.setdefault("pyautogui", _fake_pyautogui)

# Now safe to import the module under test.
sys.path.insert(0, "No Screensaver")
import noscreensaver  # noqa: E402  (import after sys.path manipulation)


class TestKeepAwakeSmallestInput(unittest.TestCase):
    """keep_awake with the smallest valid inputs: interval=1, x=0, y=0."""

    def setUp(self):
        _fake_pyautogui.sleep.reset_mock()
        _fake_pyautogui.click.reset_mock()

    def test_sleep_called_with_smallest_interval(self):
        """pyautogui.sleep receives interval_seconds=1 (smallest valid)."""
        # Precondition anchor: import pyautogui  # line 1
        # Expected: sleep(1) called exactly once
        noscreensaver.keep_awake(interval_seconds=1, click_x=0, click_y=0)
        _fake_pyautogui.sleep.assert_called_once_with(1)

    def test_click_called_with_smallest_coords(self):
        """pyautogui.click receives (0, 0) (smallest valid co-ordinates)."""
        # Precondition anchor: import pyautogui  # line 1
        # Expected: click(0, 0) called exactly once
        noscreensaver.keep_awake(interval_seconds=1, click_x=0, click_y=0)
        _fake_pyautogui.click.assert_called_once_with(0, 0)

    def test_return_value_is_none_smallest(self):
        """keep_awake returns None for smallest inputs."""
        # Expected: None
        result = noscreensaver.keep_awake(interval_seconds=1, click_x=0, click_y=0)
        self.assertIsNone(result)

    def test_sleep_before_click_smallest(self):
        """sleep is called before click (order preserved, smallest inputs)."""
        manager = MagicMock()
        manager.attach_mock(_fake_pyautogui.sleep, "sleep")
        manager.attach_mock(_fake_pyautogui.click, "click")
        noscreensaver.keep_awake(interval_seconds=1, click_x=0, click_y=0)
        expected_order = [call.sleep(1), call.click(0, 0)]
        self.assertEqual(manager.mock_calls, expected_order)


class TestKeepAwakeOrdinaryInput(unittest.TestCase):
    """keep_awake with the ordinary inputs: interval=40, x=50, y=400."""

    def setUp(self):
        _fake_pyautogui.sleep.reset_mock()
        _fake_pyautogui.click.reset_mock()

    def test_sleep_called_with_ordinary_interval(self):
        """pyautogui.sleep receives interval_seconds=40 (ordinary input)."""
        # Precondition anchor: import pyautogui  # line 1
        # Expected: sleep(40) called exactly once
        noscreensaver.keep_awake(interval_seconds=40, click_x=50, click_y=400)
        _fake_pyautogui.sleep.assert_called_once_with(40)

    def test_click_called_with_ordinary_coords(self):
        """pyautogui.click receives (50, 400) (ordinary co-ordinates)."""
        # Precondition anchor: import pyautogui  # line 1
        # Expected: click(50, 400) called exactly once
        noscreensaver.keep_awake(interval_seconds=40, click_x=50, click_y=400)
        _fake_pyautogui.click.assert_called_once_with(50, 400)

    def test_return_value_is_none_ordinary(self):
        """keep_awake returns None for ordinary inputs."""
        # Expected: None
        result = noscreensaver.keep_awake(interval_seconds=40, click_x=50, click_y=400)
        self.assertIsNone(result)

    def test_sleep_before_click_ordinary(self):
        """sleep is called before click (order preserved, ordinary inputs)."""
        manager = MagicMock()
        manager.attach_mock(_fake_pyautogui.sleep, "sleep")
        manager.attach_mock(_fake_pyautogui.click, "click")
        noscreensaver.keep_awake(interval_seconds=40, click_x=50, click_y=400)
        expected_order = [call.sleep(40), call.click(50, 400)]
        self.assertEqual(manager.mock_calls, expected_order)


class TestKeepAwakeDefaultsPreserved(unittest.TestCase):
    """Default argument values must match the original hard-coded values."""

    def setUp(self):
        _fake_pyautogui.sleep.reset_mock()
        _fake_pyautogui.click.reset_mock()

    def test_defaults_match_original_hardcoded_values(self):
        """Calling keep_awake() with no args replicates original behaviour."""
        # Original code: pyautogui.sleep(40); pyautogui.click(50, 400)
        # Expected defaults: interval_seconds=40, click_x=50, click_y=400
        noscreensaver.keep_awake()
        _fake_pyautogui.sleep.assert_called_once_with(40)
        _fake_pyautogui.click.assert_called_once_with(50, 400)

    def test_isolated_calls_do_not_share_state(self):
        """Two consecutive calls are independent — no shared mutable state."""
        noscreensaver.keep_awake(interval_seconds=1, click_x=0, click_y=0)
        _fake_pyautogui.sleep.reset_mock()
        _fake_pyautogui.click.reset_mock()
        noscreensaver.keep_awake(interval_seconds=40, click_x=50, click_y=400)
        # Second call uses its own arguments, not those from the first.
        _fake_pyautogui.sleep.assert_called_once_with(40)
        _fake_pyautogui.click.assert_called_once_with(50, 400)


if __name__ == "__main__":
    unittest.main()
