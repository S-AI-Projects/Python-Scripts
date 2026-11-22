"""Focused tests for Auto WiFi Check; all OS/network effects are mocked."""

import ctypes
import io
import json
import logging
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, mock_open, patch


WORK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = WORK_DIR.parents[1]
MODULE_PATH = REPO_ROOT / "Auto WiFi Check" / "wifi_checker.py"
EVIDENCE = []


class _ImportLoopReached(Exception):
    """Stops the target module's top-level scheduler loop during import."""


def load_wifi_checker(source_text, source_name):
    """Execute only the named module while mocking its import-time effects."""
    schedule_stub = types.ModuleType("schedule")
    schedule_stub.every = Mock(return_value=Mock())
    schedule_stub.run_pending = Mock(side_effect=_ImportLoopReached)
    windows_stub = types.SimpleNamespace(
        shell32=types.SimpleNamespace(IsUserAnAdmin=lambda: True)
    )
    module = types.ModuleType("wifi_checker_under_test")

    with patch("builtins.open", mock_open()), \
            patch("logging.basicConfig"), \
            patch.object(ctypes, "windll", windows_stub, create=True), \
            patch.dict(sys.modules, {"schedule": schedule_stub}), \
            redirect_stdout(io.StringIO()):
        try:
            exec(compile(source_text, str(source_name), "exec"), module.__dict__)
        except _ImportLoopReached:
            pass

    return module


def load_original():
    return load_wifi_checker(MODULE_PATH.read_text(encoding="utf-8"), MODULE_PATH)


def run_always_failing_job(module):
    calls = []

    def fake_call(command, shell):
        calls.append(command)
        return 1 if command.startswith("ping ") else 0

    with patch.object(module.subprocess, "call", side_effect=fake_call), \
            patch.object(module.time, "sleep") as sleep_mock, \
            patch.object(module.logging, "info"), \
            patch.object(module.logging, "warning"), \
            patch.object(module.logging, "error"), \
            redirect_stdout(io.StringIO()):
        module.job()

    return {
        "ping_calls": sum(command.startswith("ping ") for command in calls),
        "enable_calls": calls.count("netsh interface set interface Wi-Fi enabled"),
        "disable_calls": calls.count("netsh interface set interface Wi-Fi disabled"),
        "sleep_calls": sleep_mock.call_count,
    }


class TestWifiChecker(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        evidence_path = WORK_DIR / "test_evidence.json"
        evidence_path.write_text(json.dumps(EVIDENCE, indent=2) + "\n", encoding="utf-8")

    def test_enable_success_preserves_none_result_and_calls_netsh(self):
        module = load_original()
        output = io.StringIO()
        with patch.object(module.subprocess, "call", return_value=0) as call_mock, \
                patch.object(module.logging, "info") as info_mock, \
                redirect_stdout(output):
            result = module.enable()

        actual = {
            "return": result,
            "command_call": str(call_mock.call_args),
            "stdout": output.getvalue().strip(),
            "success_log": str(info_mock.call_args),
        }
        expected = {
            "return": None,
            "command_call": "call('netsh interface set interface Wi-Fi enabled', shell=True)",
            "stdout": "Turning On the laptop WiFi",
            "success_log": "call('WiFi enabled')",
        }
        EVIDENCE.append({"case": "enable successful command", "expected": expected, "actual": actual})
        self.assertIsNone(result)
        call_mock.assert_called_once_with("netsh interface set interface Wi-Fi enabled", shell=True)
        self.assertEqual(output.getvalue().strip(), expected["stdout"])
        info_mock.assert_called_once_with("WiFi enabled")

    def test_enable_reports_nonzero_exit_without_claiming_success(self):
        module = load_original()
        output = io.StringIO()
        with patch.object(module.subprocess, "call", return_value=5) as call_mock, \
                patch.object(module.logging, "info") as info_mock, \
                patch.object(module.logging, "error") as error_mock, \
                redirect_stdout(output):
            result = module.enable()

        actual = {
            "return": result,
            "command_calls": call_mock.call_count,
            "stdout": output.getvalue().strip(),
            "success_log_calls": info_mock.call_count,
            "error_log_calls": error_mock.call_count,
        }
        expected = {
            "return": None,
            "command_calls": 1,
            "stdout_contains": "Failed to enable WiFi",
            "success_log_calls": 0,
            "error_log_calls": 1,
        }
        EVIDENCE.append({"case": "enable nonzero exit", "expected": expected, "actual": actual})
        self.assertIsNone(result)
        self.assertIn(expected["stdout_contains"], actual["stdout"])
        self.assertEqual(actual["command_calls"], 1)
        self.assertEqual(actual["success_log_calls"], 0)
        self.assertEqual(actual["error_log_calls"], 1)

    def test_enable_reports_python_exception(self):
        module = load_original()
        output = io.StringIO()
        with patch.object(module.subprocess, "call", side_effect=OSError("mocked failure")), \
                patch.object(module.logging, "info") as info_mock, \
                patch.object(module.logging, "error") as error_mock, \
                redirect_stdout(output):
            result = module.enable()

        actual = {
            "return": result,
            "stdout": output.getvalue().strip(),
            "success_log_calls": info_mock.call_count,
            "error_log_calls": error_mock.call_count,
        }
        expected = {
            "return": None,
            "stdout_contains": "Failed to enable WiFi: mocked failure",
            "success_log_calls": 0,
            "error_log_calls": 1,
        }
        EVIDENCE.append({"case": "enable raised exception", "expected": expected, "actual": actual})
        self.assertIsNone(result)
        self.assertIn(expected["stdout_contains"], actual["stdout"])
        self.assertEqual(actual["success_log_calls"], 0)
        self.assertEqual(actual["error_log_calls"], 1)

    def test_retry_limit_and_single_boundary_mutant_diverge(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        original_condition = "while attempt_counter < max_attempts:"
        mutant_condition = "while attempt_counter <= max_attempts:"
        self.assertEqual(source.count(original_condition), 1)

        original = run_always_failing_job(load_wifi_checker(source, MODULE_PATH))
        with tempfile.TemporaryDirectory(prefix="wifi-checker-mutant-") as temp_dir:
            mutant_path = Path(temp_dir) / "wifi_checker_mutant.py"
            mutant_path.write_text(source.replace(original_condition, mutant_condition, 1), encoding="utf-8")
            mutant_source = mutant_path.read_text(encoding="utf-8")
            mutant = run_always_failing_job(load_wifi_checker(mutant_source, mutant_path))

        expected = {
            "original_retries": 3,
            "mutant_retries": 4,
            "original_ping_calls_including_initial_check": 4,
            "mutant_ping_calls_including_initial_check": 5,
        }
        actual = {
            "original_retries": original["disable_calls"],
            "mutant_retries": mutant["disable_calls"],
            "original_ping_calls_including_initial_check": original["ping_calls"],
            "mutant_ping_calls_including_initial_check": mutant["ping_calls"],
            "original_call_counts": original,
            "mutant_call_counts": mutant,
            "mutant_boundary": mutant_condition,
            "temporary_copy_used": True,
        }
        EVIDENCE.append({"case": "retry boundary mutant", "expected": expected, "actual": actual})
        self.assertEqual(original["disable_calls"], expected["original_retries"])
        self.assertEqual(mutant["disable_calls"], expected["mutant_retries"])
        self.assertEqual(original["ping_calls"], expected["original_ping_calls_including_initial_check"])
        self.assertEqual(mutant["ping_calls"], expected["mutant_ping_calls_including_initial_check"])
        self.assertNotEqual(original["disable_calls"], mutant["disable_calls"])


if __name__ == "__main__":
    unittest.main(verbosity=2)