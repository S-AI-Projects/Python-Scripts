#!/usr/bin/env python3
"""Run focused, mocked tests for Auto WiFi Check and save evidence."""

import json
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path


WORK_DIR = Path(__file__).resolve().parent
REPO_ROOT = WORK_DIR.parents[1]
TEST_DIR = WORK_DIR / "tests"
TEST_PATTERN = "test_wifi_checker.py"
RUNNER_COMMAND = "python3 work/R35-T060/check.py"
NATIVE_COMMAND = [
	sys.executable,
	"-m",
	"unittest",
	"discover",
	"-s",
	str(TEST_DIR.relative_to(REPO_ROOT)),
	"-p",
	TEST_PATTERN,
	"-v",
]


PRE_CHANGE_CONTRACT = {
	"module": "Auto WiFi Check/wifi_checker.py",
	"function": "enable",
	"public_inputs": [],
	"result": "Implicitly returns None, including when subprocess.call raises.",
	"mutation_behavior": [
		"Calls subprocess.call once with the Windows netsh Wi-Fi-enable command and shell=True.",
		"Before this change, ignored the subprocess return code and could report success after a failed command.",
		"On a Python exception, prints and logs a failure; otherwise prints and logs success.",
	],
	"direct_dependencies": [
		"subprocess.call",
		"print (stdout)",
		"logging.info / logging.error",
	],
	"module_import_side_effects_to_mock": [
		"Creates/opens wifi_status_log.txt and configures logging.",
		"Checks Windows administrator state through ctypes.windll.",
		"Schedules a job and enters an infinite schedule loop.",
	],
	"module_dependencies": [
		"ctypes (standard library)",
		"subprocess (standard library)",
		"sys (standard library)",
		"time (standard library)",
		"logging (standard library)",
		"schedule (third-party; declared as schedule==1.2.2)",
	],
	"algorithm_boundary": {
		"function": "job",
		"condition_before_change": "attempt_counter < max_attempts",
		"max_attempts": 3,
		"why_used_for_mutation_check": "enable has no boundary, accumulation, or return condition to mutate.",
	},
}


def write_json(filename, value):
	path = WORK_DIR / filename
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def collect_versions(test_count):
	try:
		git_version = subprocess.check_output(
			["git", "--version"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
		).strip()
	except (OSError, subprocess.CalledProcessError):
		git_version = "unavailable"

	return {
		"python_version": sys.version,
		"python_executable": sys.executable,
		"platform": platform.platform(),
		"system": platform.system(),
		"git_version": git_version,
		"test_framework": "unittest (Python standard library; no repository pytest/tox/setup.cfg/pyproject test config found)",
		"schedule_requirement": "schedule==1.2.2",
		"schedule_test_mode": "stubbed in sys.modules; no real scheduler or Wi-Fi calls",
		"runner_command": RUNNER_COMMAND,
		"native_test_command": shlex.join(NATIVE_COMMAND),
		"nonzero_test_count": test_count,
	}


def run_native_tests():
	command_text = shlex.join(NATIVE_COMMAND)
	print(f"[check] Native focused test command: {command_text}")
	process = subprocess.run(
		NATIVE_COMMAND,
		cwd=REPO_ROOT,
		capture_output=True,
		text=True,
		check=False,
	)
	output = process.stdout + process.stderr
	print(output, end="" if output.endswith("\n") else "\n")

	match = re.search(r"Ran (\d+) tests? in ", output)
	test_count = int(match.group(1)) if match else 0
	evidence_path = WORK_DIR / "test_evidence.json"
	evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else []

	return {
		"command": command_text,
		"exit_code": process.returncode,
		"test_count": test_count,
		"output": output,
		"evidence": evidence,
	}


def main():
	WORK_DIR.mkdir(parents=True, exist_ok=True)
	inputs = {
		"pre_change_contract": PRE_CHANGE_CONTRACT,
		"enable_checks": [
			{"case": "successful command", "arguments": [], "mocked_netsh_exit_code": 0},
			{"case": "command reports failure", "arguments": [], "mocked_netsh_exit_code": 5},
			{"case": "command raises", "arguments": [], "mocked_exception": "OSError"},
		],
		"reduced_retry_input": {
			"initial_ping_exit_code": 1,
			"every_retry_ping_exit_code": 1,
			"other_state": "fixed or mocked; no real network, sleep, scheduler, file, or OS calls",
			"reduction": "One constant failure response replaces arbitrary ping histories; only the retry bound and number of retries are observed.",
		},
		"mutant": {
			"temporary_copy_only": True,
			"single_change": "attempt_counter < max_attempts -> attempt_counter <= max_attempts",
			"reason": "enable contains no algorithmic boundary; job owns the bounded retry loop in this same named module.",
		},
		"independent_expected_result": {
			"original_retries": 3,
			"mutant_retries": 4,
			"derivation": "The counter starts at 0 and increases once after each failed retry. The strict condition permits values 0, 1, and 2; the mutated inclusive condition also permits 3.",
		},
	}
	write_json("inputs.json", inputs)

	result = run_native_tests()
	versions = collect_versions(result["test_count"])
	write_json("tool_versions.json", versions)

	expected_vs_actual = {
		"runner_command": RUNNER_COMMAND,
		"native_test_command": result["command"],
		"expected": {
			"tests_run": "> 0",
			"test_exit_code": 0,
			"original_retry_count": 3,
			"mutant_retry_count": 4,
		},
		"actual": {
			"tests_run": result["test_count"],
			"test_exit_code": result["exit_code"],
			"evidence": result["evidence"],
			"test_output": result["output"],
		},
	}
	write_json("expected_vs_actual.json", expected_vs_actual)

	if result["exit_code"] != 0 or result["test_count"] <= 0:
		print("[check] Focused tests failed or no tests were collected.", file=sys.stderr)
		return result["exit_code"] or 1

	print(f"[check] All focused tests passed ({result['test_count']} tests). Artifacts saved in {WORK_DIR}.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
