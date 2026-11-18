import os
import re
import sys
import time as time_module
import unittest
from unittest.mock import MagicMock

# Ensure Digital Clock directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import DigitalClock as dc


class TestDigitalClockInvariants(unittest.TestCase):
    """
    Focused invariant property tests for Digital Clock (DigitalClock.py).
    Precondition source lines:
      - DigitalClock.py:2 establishes strftime import
      - DigitalClock.py:4 establishes TIME_FORMAT = '%H: %M: %S %p'
      - DigitalClock.py:7 establishes format_time
      - DigitalClock.py:27 establishes time
    """

    def test_preconditions(self):
        self.assertEqual(dc.TIME_FORMAT, "%H: %M: %S %p")

    def test_smallest_valid_input_midnight(self):
        # Smallest valid input: midnight (00:00:00 AM)
        midnight_t = time_module.struct_time((2026, 1, 1, 0, 0, 0, 3, 1, 0))
        result = dc.format_time(midnight_t)
        self.assertEqual(result, "00: 00: 00 AM")
        self.assertEqual(len(result), 13)

    def test_ordinary_valid_input_afternoon(self):
        # Ordinary input: 14:30:45 PM
        afternoon_t = time_module.struct_time((2026, 11, 18, 14, 30, 45, 2, 322, 0))
        result = dc.format_time(afternoon_t)
        self.assertEqual(result, "14: 30: 45 PM")
        self.assertEqual(len(result), 13)

    def test_invariant_properties_across_generated_domain(self):
        # Verify invariant across all 24 hours with representative minute/second boundaries
        pattern = re.compile(r"^(\d{2}): (\d{2}): (\d{2}) (AM|PM)$")

        sample_cases = []
        for h in range(24):
            for m, s in [(0, 0), (15, 30), (45, 10), (59, 59)]:
                sample_cases.append((h, m, s))

        for h, m, s in sample_cases:
            t_struct = time_module.struct_time((2026, 6, 15, h, m, s, 0, 166, 0))
            formatted = dc.format_time(t_struct)

            # Invariant 1: Type and length
            self.assertIsInstance(formatted, str)
            self.assertEqual(len(formatted), 13, f"Failed length invariant for {h}:{m}:{s}")

            # Invariant 2: Regex structure
            match = pattern.match(formatted)
            self.assertIsNotNone(match, f"Pattern mismatch for {formatted}")

            hh_str, mm_str, ss_str, period = match.groups()
            hh, mm, ss = int(hh_str), int(mm_str), int(ss_str)

            # Invariant 3: Value preservation
            self.assertEqual(hh, h)
            self.assertEqual(mm, m)
            self.assertEqual(ss, s)

            # Invariant 4: AM/PM rule
            expected_period = "AM" if h < 12 else "PM"
            self.assertEqual(period, expected_period)

    def test_time_updates_label_and_schedules_after(self):
        mock_label = MagicMock()
        fixed_t = time_module.struct_time((2026, 11, 18, 9, 15, 30, 2, 322, 0))

        result = dc.time(
            label=mock_label,
            strftime_func=lambda fmt: time_module.strftime(fmt, fixed_t),
        )

        self.assertEqual(result, "09: 15: 30 AM")
        mock_label.config.assert_called_once_with(text="09: 15: 30 AM")
        mock_label.after.assert_called_once()
        self.assertEqual(mock_label.after.call_args[0][0], 1000)


if __name__ == "__main__":
    unittest.main()
