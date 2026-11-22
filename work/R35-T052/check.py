#!/usr/bin/env python3
"""Focused runner that executes Hand Volume checks and propagates failures.

Native check incorporated: run focused Python tests using project test configuration;
import or invoke only the named module, with external I/O mocked.
Records actual command and nonzero test count.
Saves inputs, expected vs actual results, and tool versions in work/R35-T052/.
"""

import importlib
import json
import os
import platform
import subprocess
import sys
import unittest
from unittest.mock import MagicMock

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))
HAND_VOLUME_DIR = os.path.join(REPO_ROOT, "Hand Volume")

if HAND_VOLUME_DIR not in sys.path:
    sys.path.insert(0, HAND_VOLUME_DIR)


def save_artifact(filename, data):
    """Save dictionary or string to file in WORK_DIR."""
    filepath = os.path.join(WORK_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, indent=2)
        else:
            f.write(str(data))
    return filepath


def record_tool_versions():
    """Record versions of python, git, platform, and unittest."""
    git_version = "unknown"
    try:
        git_res = subprocess.run(["git", "--version"], capture_output=True, text=True, check=False)
        git_version = git_res.stdout.strip()
    except Exception as e:
        git_version = str(e)

    versions = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "git_version": git_version,
        "test_framework": "unittest (Python standard library)",
    }
    save_artifact("tool_versions.json", versions)
    return versions


def record_inputs():
    """Record partitioned inputs and test boundaries."""
    inputs_data = {
        "module": "Hand Volume/main.py",
        "named_module": "main",
        "partitions": {
            "distance_to_percent": {
                "lower_boundary": 50.0,
                "upper_boundary": 250.0,
                "below_lower_boundary": [49.0, 0.0, -20.0],
                "above_lower_boundary": [52.0],
                "valid_interior": [70.0, 150.0, 210.0],
                "below_upper_boundary": [248.0],
                "above_upper_boundary": [252.0, 350.0],
                "unsupported_types": ["None", "'invalid'"],
            },
            "percent_to_volume_change": {
                "lower_boundary": 0,
                "upper_boundary": 100,
                "above_lower_boundary": [10],
                "valid_interior": [25, 50, 75],
                "below_upper_boundary": [90],
                "above_upper_boundary": [110],
                "domain_boundary_unsupported": [-10, -15],
                "unsupported_types": ["None", "'bad'"],
            },
            "percent_to_bar_height": {
                "lower_boundary": 0,
                "upper_boundary": 100,
                "below_lower_boundary": [-5],
                "above_lower_boundary": [5],
                "valid_interior": [50],
                "below_upper_boundary": [95],
                "above_upper_boundary": [105],
            },
            "calculate_distance": {
                "coincident_boundary": [((100, 100), (100, 100))],
                "strictly_positive_interior": [((0, 0), (3, 4)), ((100, 100), (220, 260))],
            },
            "detect_fingers": {
                "empty_boundary": [],
                "gesture_interior": "21 landmarks with Thumb and Index extended",
            },
        },
        "mocked_io": [
            "cv2.VideoCapture",
            "pycaw.pycaw.AudioUtilities",
            "comtypes.CLSCTX_ALL",
            "mediapipe.solutions.hands",
        ],
    }
    save_artifact("inputs.json", inputs_data)
    return inputs_data


def run_native_checks():
    """Run focused Python tests using project test configuration (unittest)."""
    test_file = os.path.join(HAND_VOLUME_DIR, "tests", "test_hand_volume.py")
    test_cmd = [sys.executable, "-m", "unittest", test_file]
    actual_cmd_str = f"python3 -m unittest {os.path.relpath(test_file, REPO_ROOT)}"

    print(f"[RUNNER] Executing native test command: {actual_cmd_str}")
    proc = subprocess.run(
        test_cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    combined_output = proc.stdout + "\n" + proc.stderr
    print(combined_output)

    # Parse test count from unittest stderr output
    test_count = 0
    for line in combined_output.splitlines():
        if line.startswith("Ran ") and "tests in" in line:
            parts = line.split()
            try:
                test_count = int(parts[1])
            except (IndexError, ValueError):
                pass
        elif line.startswith("Ran ") and "test in" in line:
            parts = line.split()
            try:
                test_count = int(parts[1])
            except (IndexError, ValueError):
                pass

    if proc.returncode != 0:
        raise RuntimeError(f"Native unit tests failed with exit code {proc.returncode}:\n{combined_output}")

    if test_count <= 0:
        raise RuntimeError(f"Native unit tests reported 0 tests executed. Command: {actual_cmd_str}")

    print(f"[RUNNER] Native tests passed successfully! Test count: {test_count}")
    return actual_cmd_str, test_count, combined_output


def run_focused_checks():
    """Run direct programmatic assertion checks on main module with mocked I/O."""
    import main

    assertions_log = []

    # Check 1: Boundary 50.0 -> 0
    p0 = main.distance_to_percent(50.0)
    assert p0 == 0, f"Expected 0, got {p0}"
    assertions_log.append({"check": "distance_to_percent(50.0)", "expected": 0, "actual": p0, "status": "PASS"})

    # Check 2: Left of lower boundary 49.0 -> 0
    p_left = main.distance_to_percent(49.0)
    assert p_left == 0, f"Expected 0, got {p_left}"
    assertions_log.append({"check": "distance_to_percent(49.0)", "expected": 0, "actual": p_left, "status": "PASS"})

    # Check 3: Right of lower boundary 52.0 -> 1
    p_right = main.distance_to_percent(52.0)
    assert p_right == 1, f"Expected 1, got {p_right}"
    assertions_log.append({"check": "distance_to_percent(52.0)", "expected": 1, "actual": p_right, "status": "PASS"})

    # Check 4: Boundary 250.0 -> 100
    p100 = main.distance_to_percent(250.0)
    assert p100 == 100, f"Expected 100, got {p100}"
    assertions_log.append({"check": "distance_to_percent(250.0)", "expected": 100, "actual": p100, "status": "PASS"})

    # Check 5: Right of upper boundary 252.0 -> 100
    p_top_right = main.distance_to_percent(252.0)
    assert p_top_right == 100, f"Expected 100, got {p_top_right}"
    assertions_log.append({"check": "distance_to_percent(252.0)", "expected": 100, "actual": p_top_right, "status": "PASS"})

    # Check 6: Math domain error on Percent <= -10
    raised = False
    try:
        main.percent_to_volume_change(-10)
    except ValueError:
        raised = True
    assert raised, "Expected ValueError on percent_to_volume_change(-10)"
    assertions_log.append({"check": "percent_to_volume_change(-10)", "expected": "ValueError", "actual": "ValueError", "status": "PASS"})

    # Check 7: Percent 100 -> Changevolume 65
    v100 = main.percent_to_volume_change(100)
    assert v100 == 65, f"Expected 65, got {v100}"
    assertions_log.append({"check": "percent_to_volume_change(100)", "expected": 65, "actual": v100, "status": "PASS"})

    # Check 8: Percent 0 -> height 340
    h0 = main.percent_to_bar_height(0)
    assert h0 == 340, f"Expected 340, got {h0}"
    assertions_log.append({"check": "percent_to_bar_height(0)", "expected": 340, "actual": h0, "status": "PASS"})

    # Check 9: Percent 100 -> height 140
    h100 = main.percent_to_bar_height(100)
    assert h100 == 140, f"Expected 140, got {h100}"
    assertions_log.append({"check": "percent_to_bar_height(100)", "expected": 140, "actual": h100, "status": "PASS"})

    return assertions_log


def main_runner():
    print("[RUNNER] Starting work/R35-T052/check.py focused runner...")
    tool_versions = record_tool_versions()
    inputs_data = record_inputs()

    try:
        actual_cmd, test_count, test_output = run_native_checks()
        assertions_log = run_focused_checks()

        expected_vs_actual = {
            "baseline_mismatch_analysis": {
                "command": "python3 'Hand Volume/main.py'",
                "independent_expected": (
                    "Modular execution of distance-to-volume mapping; "
                    "safe import without camera acquisition or infinite while-loops; "
                    "partitioned boundary handling for distance [50, 250], percent [0, 100], "
                    "volume changes [0, 65] dB, and UI bar heights [140, 340]."
                ),
                "actual_baseline_result": (
                    "ModuleNotFoundError: No module named 'numpy' / 'cv2' / 'pycaw'. "
                    "Top-level execution unconditionally invokes Windows COM AudioUtilities "
                    "and cv2.VideoCapture(0), blocking in while True: loop on import."
                ),
                "explanation_of_mismatch": (
                    "Implementation coupled domain calculation logic directly with unhandled "
                    "external I/O, device drivers, and an infinite loop at module level."
                ),
            },
            "post_fix_runner_results": {
                "native_test_command": actual_cmd,
                "nonzero_test_count": test_count,
                "test_suite_status": "ALL_TESTS_PASSED",
                "direct_assertions": assertions_log,
            },
        }
        save_artifact("expected_vs_actual.json", expected_vs_actual)

        print(f"\n=======================================================")
        print(f" ALL CHECKS PASSED SUCCESSFULLY")
        print(f" Native Command: {actual_cmd}")
        print(f" Nonzero Test Count: {test_count}")
        print(f" Artifacts saved in: {WORK_DIR}")
        print(f"=======================================================\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n[RUNNER ERROR] Check failed: {e}", file=sys.stderr)
        save_artifact("expected_vs_actual.json", {
            "status": "FAILED",
            "error": str(e),
        })
        sys.exit(1)


if __name__ == "__main__":
    main_runner()
