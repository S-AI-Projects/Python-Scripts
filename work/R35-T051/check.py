#!/usr/bin/env python3
"""Focused runner that executes Font Art checks and propagates failures.

Native check incorporated: run focused Python tests using project test configuration;
import or invoke only the named module, with external I/O mocked.
Records actual command and nonzero test count.
Saves inputs, expected vs actual results, and tool versions in work/R35-T051/.
"""

import importlib
import io
import json
import os
import platform
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, call, patch

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))
FONT_ART_DIR = os.path.join(REPO_ROOT, "Font Art")

if FONT_ART_DIR not in sys.path:
    sys.path.insert(0, FONT_ART_DIR)


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
    """Record inputs and test fixtures."""
    inputs_data = {
        "module": "Font Art/FontArt.py",
        "named_module": "FontArt",
        "public_inputs": {
            "default_text": "Dhanush N",
            "default_font": "slant",
            "windows_console_cols": 75,
            "windows_console_lines": 30,
        },
        "functions": {
            "render_font_art": {
                "parameters": ["text (default: 'Dhanush N')", "font (default: 'slant')"],
                "return_type": "str",
            },
            "display_font_art": {
                "parameters": [
                    "text (default: 'Dhanush N')",
                    "font (default: 'slant')",
                    "cols (default: 75)",
                    "lines (default: 30)",
                ],
                "return_type": "str",
            },
            "main": {
                "parameters": [],
                "return_type": "None",
            },
        },
        "fixtures": {
            "default_expected_ascii_art": (
                "    ____  __                                __       _   __\n"
                "   / __ \\/ /_  ____ _____  __  ___________ / /_     / | / /\n"
                "  / / / / __ \\/ __ `/ __ \\/ / / / ___/ __ \\/ __ \\   /  |/ / \n"
                " / /_/ / / / / /_/ / / / / /_/ (__  ) / / / / / /  / /|  /  \n"
                "/_____/_/ /_/\\__,_/_/ /_/\\__,_/____/_/ /_/_/ /_/  /_/ |_/   \n"
            ),
            "custom_text": "Custom Message",
            "custom_font": "banner",
            "custom_expected_art": "CUSTOM_ASCII_ART",
        },
        "mocked_io": [
            "pyfiglet.Figlet",
            "os.system",
            "sys.stdout",
        ],
    }
    save_artifact("inputs.json", inputs_data)
    return inputs_data


def run_native_checks():
    """Run focused Python tests using project test configuration (unittest)."""
    test_file = os.path.join(FONT_ART_DIR, "tests", "test_font_art.py")
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

    # Parse test count from unittest stderr output (e.g. "Ran 7 tests in 0.005s")
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
    """Run direct programmatic assertion checks on FontArt module with mocked I/O."""
    assertions_log = []

    mock_figlet_cls = MagicMock()
    mock_figlet_inst = MagicMock()
    mock_figlet_cls.return_value = mock_figlet_inst
    expected_art = (
        "    ____  __                                __       _   __\n"
        "   / __ \\/ /_  ____ _____  __  ___________ / /_     / | / /\n"
        "  / / / / __ \\/ __ `/ __ \\/ / / / ___/ __ \\/ __ \\   /  |/ / \n"
        " / /_/ / / / / /_/ / / / / /_/ (__  ) / / / / / /  / /|  /  \n"
        "/_____/_/ /_/\\__,_/_/ /_/\\__,_/____/_/ /_/_/ /_/  /_/ |_/   \n"
    )
    mock_figlet_inst.renderText.return_value = expected_art

    with patch.dict(sys.modules, {"pyfiglet": MagicMock(Figlet=mock_figlet_cls)}):
        import FontArt
        with patch.object(FontArt, "Figlet", mock_figlet_cls):
            # Check 1: render_font_art content
            art = FontArt.render_font_art()
            assert art == expected_art, f"Rendered art mismatch: expected {expected_art!r}, got {art!r}"
            mock_figlet_cls.assert_called_with(font="slant")
            mock_figlet_inst.renderText.assert_called_with("Dhanush N")
            assertions_log.append({
                "name": "render_font_art_default_content",
                "expected": expected_art,
                "actual": art,
                "status": "PASS",
            })

            # Check 2: Windows display behavior
            with patch("os.name", "nt"), \
                 patch("os.system") as mock_sys, \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                ret = FontArt.display_font_art()
                assert mock_sys.call_args_list == [call("cls"), call("mode con: cols=75 lines=30")], \
                    f"Unexpected os.system calls on Windows: {mock_sys.call_args_list}"
                assert mock_out.getvalue() == f"{expected_art}\n", \
                    f"Unexpected stdout on Windows: {mock_out.getvalue()!r}"
                assertions_log.append({
                    "name": "display_font_art_windows_os_calls",
                    "expected": ["cls", "mode con: cols=75 lines=30"],
                    "actual": [c[0][0] for c in mock_sys.call_args_list],
                    "status": "PASS",
                })

            # Check 3: POSIX display behavior
            with patch("os.name", "posix"), \
                 patch("os.system") as mock_sys, \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                ret = FontArt.display_font_art()
                assert mock_sys.call_args_list == [call("clear")], \
                    f"Unexpected os.system calls on POSIX: {mock_sys.call_args_list}"
                assert mock_out.getvalue() == f"{expected_art}\n", \
                    f"Unexpected stdout on POSIX: {mock_out.getvalue()!r}"
                assertions_log.append({
                    "name": "display_font_art_posix_os_calls",
                    "expected": ["clear"],
                    "actual": [c[0][0] for c in mock_sys.call_args_list],
                    "status": "PASS",
                })

            # Check 4: Safe import with no side effects
            with patch("os.system") as mock_sys, \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                importlib.reload(FontArt)
                assert mock_sys.call_count == 0, f"Expected 0 os.system calls on import, got {mock_sys.call_count}"
                assert mock_out.getvalue() == "", f"Expected empty stdout on import, got {mock_out.getvalue()!r}"
                assertions_log.append({
                    "name": "safe_import_no_side_effects",
                    "expected": "0 os.system calls and empty stdout",
                    "actual": f"{mock_sys.call_count} calls, stdout length {len(mock_out.getvalue())}",
                    "status": "PASS",
                })

    return assertions_log


def main():
    print("[RUNNER] Starting work/R35-T051/check.py focused runner...")
    tool_versions = record_tool_versions()
    inputs_data = record_inputs()

    try:
        actual_cmd, test_count, test_output = run_native_checks()
        assertions_log = run_focused_checks()

        expected_vs_actual = {
            "baseline_mismatch_analysis": {
                "command": "python3 'Font Art/FontArt.py'",
                "fixture_input": {
                    "text": "Dhanush N",
                    "font": "slant",
                    "target_platform": "Cross-platform (Windows & POSIX)",
                },
                "independent_expected": (
                    "Render ASCII art for 'Dhanush N' using 'slant' font; "
                    "clear terminal using platform-appropriate command ('clear' on POSIX, 'cls' on Windows); "
                    "configure console dimensions only on Windows; "
                    "safe import without uncontrolled side effects; "
                    "graceful dependency handling with declared requirements.txt"
                ),
                "actual_baseline_result": (
                    "ModuleNotFoundError: No module named 'pyfiglet' on clean environment. "
                    "On POSIX systems when pyfiglet exists: 'sh: cls: command not found' (exit code 32512), "
                    "'sh: mode: command not found' (exit code 32512). "
                    "Top-level script executes side-effects on import."
                ),
                "explanation_of_mismatch": (
                    "Baseline assumed a Windows environment and unmanaged pyfiglet installation. "
                    "Unconditionally invoked Windows-only 'cls' and 'mode con:' commands, "
                    "lacked requirements.txt, and had no function encapsulation or __name__ == '__main__' guard."
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
    main()
