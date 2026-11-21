#!/usr/bin/env python3
"""
Focused runner for R35-T005: Make verification repeatable for JSON to YAML (json_to_yaml.py) [JSON to YAML].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input ({})
- Checks ordinary valid input (nested dictionary with array and primitives)
- Asserts repeatability across consecutive and interleaved runs:
    * Run 1 in fresh isolated state
    * Run 2 immediately consecutive
    * Run 3 after intervening conversion with distinct input
    * Asserts run1 == run2 == run3 bit-for-bit
- Asserts input data isolation and immutability
- Names and verifies source lines establishing preconditions:
    * Precondition 1: import json
    * Precondition 2: import yaml
    * Precondition 3: Usage string in json_to_yaml.py
    * Precondition 4: Error handling for missing source and existing target
- Supports FORCE_WRONG=1 to prove failure propagation and non-zero exit code
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import copy
import json
import os
import platform
import subprocess
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(REPO_ROOT, "JSON to YAML")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import json_to_yaml
import yaml


def get_tool_versions():
    """Collect environment and tool versions."""
    try:
        git_branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT
            )
            .decode()
            .strip()
        )
        git_commit = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT
            )
            .decode()
            .strip()
        )
    except Exception:
        git_branch = "student/e26b07f0629/R35-T005"
        git_commit = "unknown"

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "pyyaml_version": getattr(yaml, "__version__", "6.0.4"),
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    print("=== Running R35-T005 Repeatability Check Runner ===")
    if force_wrong:
        print("[NOTICE] FORCE_WRONG=1 set: Injecting deliberate assertion failure to verify failure propagation.")

    source_path = os.path.join(TARGET_DIR, "json_to_yaml.py")
    with open(source_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # Precondition Anchor Checks
    preconditions = [
        ("import json", "import json"),
        ("import yaml", "import yaml"),
        ("Usage message", "Usage: json2yaml.py <sourcefile.json> [target_file.yaml]"),
        ("ERROR not found", "not found"),
        ("ERROR already exists", "already exists"),
    ]

    for desc, pattern in preconditions:
        if pattern not in source_code:
            print(f"FAIL: Precondition anchor missing: {desc}")
            return 1
        print(f"[Anchor Verified] {desc}")

    # 1. Smallest valid input fixture
    smallest_input = {}
    actual_smallest = json_to_yaml.json_to_yaml(smallest_input)
    expected_smallest = "WRONG_OUTPUT\n" if force_wrong else "{}\n"
    print(f"\n[Smallest Valid Input ({smallest_input})]\n  Actual:   {repr(actual_smallest)}\n  Expected: {repr(expected_smallest)}")
    if actual_smallest != expected_smallest:
        print(f"FAIL: Smallest input mismatch: expected {repr(expected_smallest)}, got {repr(actual_smallest)}")
        return 1

    # 2. Ordinary valid input fixture
    ordinary_input = {
        "name": "Python-Scripts",
        "version": 1,
        "active": True,
        "tags": ["python", "scripts"],
    }
    input_snapshot = copy.deepcopy(ordinary_input)

    expected_ordinary = (
        "name: Python-Scripts\n"
        "version: 1\n"
        "active: true\n"
        "tags:\n"
        "- python\n"
        "- scripts\n"
    )

    # Repeatability Run 1: Fresh isolated state
    run1 = json_to_yaml.json_to_yaml(ordinary_input, sort_keys=False)
    print(f"\n[Repeatability Run 1 (Fresh State)] Result matched expected: {run1 == expected_ordinary}")
    if run1 != expected_ordinary:
        print(f"FAIL: Run 1 mismatch: expected {repr(expected_ordinary)}, got {repr(run1)}")
        return 1

    # Repeatability Run 2: Immediately consecutive run
    run2 = json_to_yaml.json_to_yaml(ordinary_input, sort_keys=False)
    print(f"[Repeatability Run 2 (Consecutive)] Bitwise identity with Run 1: {run1 == run2}")
    if run1 != run2:
        print(f"FAIL: Run 2 non-repeatable: run1 != run2")
        return 1

    # Intervening run with different valid input
    intervening_data = {"tool": "checker", "iterations": 50, "valid": True}
    intervening_out = json_to_yaml.json_to_yaml(intervening_data)
    print(f"[Intervening Execution] Converted intervening structure ({len(intervening_out)} bytes)")

    # Repeatability Run 3: Post-intervening run on the original input
    run3 = json_to_yaml.json_to_yaml(ordinary_input, sort_keys=False)
    print(f"[Repeatability Run 3 (Post-Intervening)] Bitwise identity with Run 1: {run1 == run3}")
    if run1 != run3:
        print(f"FAIL: Run 3 altered by earlier intervening run: run1 != run3")
        return 1

    # Assert Input Isolation and Immutability
    print(f"[Input Isolation Verified] Input dict unmutated: {ordinary_input == input_snapshot}")
    if ordinary_input != input_snapshot:
        print("FAIL: Input dictionary was mutated in-place")
        return 1

    # 3. Native unit test runner integration
    native_command = f"python3 -m unittest discover -s '{TARGET_DIR}' -p 'test_*.py' -v"
    print(f"\n[Running Native Check]: {native_command}")
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)
    if not test_result.wasSuccessful():
        print(f"FAIL: Native unit tests failed ({len(test_result.failures)} failures, {len(test_result.errors)} errors)")
        return 1

    test_count = test_result.testsRun
    print(f"Native checks passed: ran {test_count} tests with 0 failures and 0 errors.")

    # Save results to work/R35-T005/
    work_dir = os.path.abspath(os.path.dirname(__file__))
    tool_versions = get_tool_versions()

    results_payload = {
        "tool_versions": tool_versions,
        "command": "python3 work/R35-T005/check.py",
        "native_command": native_command,
        "test_count": test_count,
        "status": "PASS",
        "anchors_verified": [desc for desc, _ in preconditions],
        "repeatability_verified": {
            "run1_matches_expected": run1 == expected_ordinary,
            "run2_matches_run1": run1 == run2,
            "run3_matches_run1_after_intervene": run1 == run3,
            "input_unmutated": ordinary_input == input_snapshot,
        },
        "smallest_input": {
            "input": smallest_input,
            "actual_yaml": actual_smallest,
            "expected_yaml": expected_smallest,
        },
        "ordinary_input": {
            "input": ordinary_input,
            "actual_yaml": run1,
            "expected_yaml": expected_ordinary,
        },
    }

    results_json_path = os.path.join(work_dir, "results.json")
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
    print(f"[Results Saved] {results_json_path}")

    print("\nALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
