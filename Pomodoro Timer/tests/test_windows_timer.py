import contextlib
import importlib.util
import io
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "Pomodoro Timer Windows.py"


class TestPomodoroTimerWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_winsound = types.ModuleType("winsound")
        fake_winsound.Beep = lambda frequency, duration: None
        with patch.dict(sys.modules, {"winsound": fake_winsound}):
            spec = importlib.util.spec_from_file_location(
                "pomodoro_timer_windows", SCRIPT_PATH
            )
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def run_timer(self, *args, **kwargs):
        events = []
        output = io.StringIO()

        def sleep(seconds):
            events.append(("sleep", seconds))

        def beep(frequency, duration):
            events.append(("beep", frequency, duration))

        with patch.object(self.module.time, "sleep", side_effect=sleep), patch.object(
            self.module.winsound, "Beep", side_effect=beep
        ), contextlib.redirect_stdout(output):
            result = self.module.pomodoro_timer_windows(*args, **kwargs)

        return result, events, output.getvalue().splitlines()

    def test_two_custom_cycles_follow_work_break_intermediate_states(self):
        expected = (
            None,
            [
                ("sleep", 120),
                ("beep", 1000, 1000),
                ("sleep", 60),
                ("beep", 1000, 1000),
                ("sleep", 120),
                ("beep", 1000, 1000),
                ("sleep", 60),
                ("beep", 1000, 1000),
            ],
            [
                "Cycle 1/2: Start working for 2 minutes.",
                "Time's up! Take a break.",
                "Break time! Relax for 1 minutes.",
                "Break is over! Back to work.",
                "Cycle 2/2: Start working for 2 minutes.",
                "Time's up! Take a break.",
                "Break time! Relax for 1 minutes.",
                "Break is over! Back to work.",
                "All cycles completed! Great job!",
            ],
        )

        actual = self.run_timer(work_duration=2, break_duration=1, cycles=2)

        self.assertEqual(actual, expected)

    def test_default_arguments_run_four_full_cycles(self):
        expected_events = [
            event
            for _ in range(4)
            for event in (
                ("sleep", 1500),
                ("beep", 1000, 1000),
                ("sleep", 300),
                ("beep", 1000, 1000),
            )
        ]
        expected_output = []
        for cycle in range(1, 5):
            expected_output.extend(
                [
                    f"Cycle {cycle}/4: Start working for 25 minutes.",
                    "Time's up! Take a break.",
                    "Break time! Relax for 5 minutes.",
                    "Break is over! Back to work.",
                ]
            )
        expected_output.append("All cycles completed! Great job!")

        actual = self.run_timer()

        self.assertEqual(actual, (None, expected_events, expected_output))

    def test_zero_cycles_only_prints_completion(self):
        expected = (None, [], ["All cycles completed! Great job!"])

        actual = self.run_timer(work_duration=2, break_duration=1, cycles=0)

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
