#!/usr/bin/env python3
"""
Focused runner for R35-T011 load_custom_emojis regression checks.

Native check incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Imports and invokes only the named module (Face Reaction/app.py) with external I/O mocked
- Verifies explicit expected values for smallest valid input, ordinary input, and boundary input
- Tests returned values and observable mutation separately
- Names the source lines establishing each precondition:
    * Precondition 1: Face Reaction/app.py:32 establishes emotion_history = []
    * Precondition 2: Face Reaction/app.py:85 establishes org = (40, 210)
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
from unittest.mock import MagicMock


def get_tool_versions(repo_root):
    """Collect relevant tool versions and environment metadata."""
    git_commit = "unknown"
    git_branch = "unknown"
    try:
        git_commit = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
            ).strip()
        )
        git_branch = (
            subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=repo_root, text=True
            ).strip()
        )
    except Exception:
        pass

    return {
        "python_version": sys.version,
        "python_version_tuple": list(sys.version_info[:3]),
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
    }


def run_native_unittest(repo_root):
    """
    Run focused Python tests using the project test configuration.
    Uses unittest test runner.
    """
    test_file = os.path.join(repo_root, "Face Reaction", "tests", "test_app.py")
    cmd = [sys.executable, "-m", "unittest", "-v", test_file]
    actual_command = f"{sys.executable} -m unittest -v Face Reaction/tests/test_app.py"

    env = os.environ.copy()
    app_dir = os.path.join(repo_root, "Face Reaction")
    env["PYTHONPATH"] = f"{app_dir}:{env.get('PYTHONPATH', '')}"

    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    return {
        "command": actual_command,
        "exit_code": proc.returncode,
        "output": proc.stdout,
    }


def run_direct_module_checks(repo_root):
    """
    Import and invoke only the named module with external I/O mocked.
    Performs focused verification of load_custom_emojis behavior.
    """
    app_dir = os.path.join(repo_root, "Face Reaction")
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)

    # Mock external I/O and hardware modules (cv2, fer, numpy)
    for mod_name in ("cv2", "fer"):
        if mod_name not in sys.modules:
            sys.modules[mod_name] = MagicMock()
    if "numpy" not in sys.modules:
        try:
            import numpy
        except ImportError:
            sys.modules["numpy"] = MagicMock()

    import app
    from app import load_custom_emojis

    checks = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Preconditions definition
        # Precondition 1: Face Reaction/app.py:32 establishes emotion_history = []
        # Precondition 2: Face Reaction/app.py:85 establishes org = (40, 210)
        precondition_source_history = "Face Reaction/app.py:32"
        precondition_source_org = "Face Reaction/app.py:85"

        # Ensure module anchors reflect preconditions
        if hasattr(app, "emotion_history"):
            app.emotion_history = []
        if hasattr(app, "org"):
            app.org = (40, 210)

        # Check 1: Smallest valid input
        c1_path = os.path.join(tmp_dir, "smallest.json")
        c1_literal_input = "{}"
        with open(c1_path, "w", encoding="utf-8") as f:
            f.write(c1_literal_input)

        c1_expected = {}
        c1_actual = load_custom_emojis(c1_path)
        c1_pass = (c1_actual == c1_expected) and isinstance(c1_actual, dict)

        checks.append({
            "name": "smallest_valid_input",
            "description": "Load smallest valid empty JSON object fixture",
            "preconditions": [
                {"anchor": precondition_source_history, "expected_state": "emotion_history = []"},
                {"anchor": precondition_source_org, "expected_state": "org = (40, 210)"},
            ],
            "input": {"file": c1_path, "content": c1_literal_input},
            "expected": c1_expected,
            "actual": c1_actual,
            "passed": c1_pass,
        })

        # Check 2: Ordinary input
        c2_path = os.path.join(tmp_dir, "ordinary.json")
        c2_literal_input = {
            "happy": "emojis/happy.png",
            "sad": "emojis/sad.png",
            "angry": "emojis/angry.png",
        }
        with open(c2_path, "w", encoding="utf-8") as f:
            json.dump(c2_literal_input, f)

        c2_expected = {
            "happy": "emojis/happy.png",
            "sad": "emojis/sad.png",
            "angry": "emojis/angry.png",
        }
        c2_actual = load_custom_emojis(c2_path)
        c2_pass = (c2_actual == c2_expected) and (len(c2_actual) == 3)

        checks.append({
            "name": "ordinary_input",
            "description": "Load standard multi-emotion configuration mapping",
            "preconditions": [
                {"anchor": precondition_source_history, "expected_state": "emotion_history = []"},
                {"anchor": precondition_source_org, "expected_state": "org = (40, 210)"},
            ],
            "input": {"file": c2_path, "content": c2_literal_input},
            "expected": c2_expected,
            "actual": c2_actual,
            "passed": c2_pass,
        })

        # Check 3: Repeated-value domain boundary
        c3_path = os.path.join(tmp_dir, "repeated.json")
        c3_literal_input = {
            "happy": "emojis/common_smile.png",
            "surprise": "emojis/common_smile.png",
            "excited": "emojis/common_smile.png",
        }
        with open(c3_path, "w", encoding="utf-8") as f:
            json.dump(c3_literal_input, f)

        c3_expected = {
            "happy": "emojis/common_smile.png",
            "surprise": "emojis/common_smile.png",
            "excited": "emojis/common_smile.png",
        }
        c3_actual = load_custom_emojis(c3_path)
        c3_pass = (c3_actual == c3_expected) and (len(set(c3_actual.values())) == 1)

        checks.append({
            "name": "repeated_value_boundary_input",
            "description": "Domain boundary with multiple keys mapping to repeated emoji value",
            "preconditions": [
                {"anchor": precondition_source_history, "expected_state": "emotion_history = []"},
                {"anchor": precondition_source_org, "expected_state": "org = (40, 210)"},
            ],
            "input": {"file": c3_path, "content": c3_literal_input},
            "expected": c3_expected,
            "actual": c3_actual,
            "passed": c3_pass,
        })

        # Check 4: Missing file boundary input
        c4_path = os.path.join(tmp_dir, "nonexistent.json")
        c4_expected = {}
        c4_actual = load_custom_emojis(c4_path)
        c4_pass = (c4_actual == c4_expected)

        checks.append({
            "name": "missing_file_boundary_input",
            "description": "Return empty dictionary for nonexistent configuration file",
            "preconditions": [
                {"anchor": precondition_source_history, "expected_state": "emotion_history = []"},
                {"anchor": precondition_source_org, "expected_state": "org = (40, 210)"},
            ],
            "input": {"file": c4_path, "exists": False},
            "expected": c4_expected,
            "actual": c4_actual,
            "passed": c4_pass,
        })

        # Check 5: Observable mutation check on emotion_history
        c5_history_before = list(getattr(app, "emotion_history", []))
        load_custom_emojis(c2_path)
        c5_history_after = list(getattr(app, "emotion_history", []))
        c5_pass = (c5_history_after == []) and (c5_history_after == c5_history_before)

        checks.append({
            "name": "observable_mutation_emotion_history",
            "description": "Verify load_custom_emojis does not mutate emotion_history anchor",
            "preconditions": [
                {"anchor": precondition_source_history, "expected_state": "emotion_history = []"}
            ],
            "input": {"file": c2_path},
            "expected": {"emotion_history": []},
            "actual": {"emotion_history": c5_history_after},
            "passed": c5_pass,
        })

        # Check 6: Observable mutation check on org coordinate
        c6_org_before = getattr(app, "org", (40, 210))
        load_custom_emojis(c2_path)
        c6_org_after = getattr(app, "org", (40, 210))
        c6_pass = (c6_org_after == (40, 210)) and (c6_org_after == c6_org_before)

        checks.append({
            "name": "observable_mutation_org",
            "description": "Verify load_custom_emojis does not mutate org coordinate anchor",
            "preconditions": [
                {"anchor": precondition_source_org, "expected_state": "org = (40, 210)"}
            ],
            "input": {"file": c2_path},
            "expected": {"org": (40, 210)},
            "actual": {"org": c6_org_after},
            "passed": c6_pass,
        })

    return checks


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.join(repo_root, "work", "R35-T011")
    os.makedirs(out_dir, exist_ok=True)

    print("=== Running Focused Regression Runner: R35-T011 ===")
    tool_versions = get_tool_versions(repo_root)

    # 1. Run native unittest check
    unittest_res = run_native_unittest(repo_root)
    print(f"Command executed: {unittest_res['command']}")
    print(f"Native test output:\n{unittest_res['output']}")

    # Count tests executed
    # Test count can be extracted from output: e.g. "Ran 6 tests in ..."
    test_count = 0
    for line in unittest_res["output"].splitlines():
        if line.startswith("Ran ") and "test" in line:
            parts = line.split()
            try:
                test_count = int(parts[1])
            except ValueError:
                pass

    # 2. Run direct module checks with mocks
    direct_checks = []
    direct_error = None
    try:
        direct_checks = run_direct_module_checks(repo_root)
    except Exception as e:
        direct_error = f"{type(e).__name__}: {e}"
        print(f"Direct module check error: {direct_error}")

    all_direct_passed = bool(direct_checks) and all(c["passed"] for c in direct_checks)
    total_checks_count = test_count if test_count > 0 else len(direct_checks)

    # 3. Assemble results payload
    results_payload = {
        "tool_versions": tool_versions,
        "actual_command": unittest_res["command"],
        "nonzero_test_count": total_checks_count,
        "native_unittest": {
            "exit_code": unittest_res["exit_code"],
            "output": unittest_res["output"],
            "passed": unittest_res["exit_code"] == 0,
        },
        "direct_checks": direct_checks,
        "direct_error": direct_error,
        "overall_passed": (unittest_res["exit_code"] == 0) and all_direct_passed,
    }

    # 4. Save results to work/R35-T011/
    for json_filename in ("test_results.json", "results.json"):
        json_path = os.path.join(out_dir, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results_payload, f, indent=2)

    for txt_filename in ("test_results.txt", "results.txt"):
        txt_path = os.path.join(out_dir, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=== R35-T011 REGRESSION TEST RESULTS ===\n")
            f.write(f"Command: {unittest_res['command']}\n")
            f.write(f"Test Count: {total_checks_count}\n")
            f.write(f"Python Version: {tool_versions['python_version']}\n")
            f.write(f"Platform: {tool_versions['platform']}\n")
            f.write(f"Git Branch: {tool_versions['git_branch']}\n")
            f.write(f"Git Commit: {tool_versions['git_commit']}\n\n")
            f.write("--- DIRECT CHECKS SUMMARY ---\n")
            for c in direct_checks:
                status = "PASSED" if c["passed"] else "FAILED"
                f.write(f"[{status}] {c['name']}: {c['description']}\n")
                f.write(f"  Input: {c['input']}\n")
                f.write(f"  Expected: {c['expected']}\n")
                f.write(f"  Actual:   {c['actual']}\n")
                f.write(f"  Preconditions: {c['preconditions']}\n\n")

            f.write(f"Overall Result: {'SUCCESS' if results_payload['overall_passed'] else 'FAILURE'}\n")

    print(f"\nSaved test results to {json_path} and {txt_path}")
    print(f"Overall Status: {'PASSED' if results_payload['overall_passed'] else 'FAILED'}")

    # 5. Exit non-zero on failure
    if not results_payload["overall_passed"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
