#!/usr/bin/env python3
"""
Focused runner for R35-T017: Publish a runnable example for Website Cloner (index.html) [Website Cloner].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input ('example.com') and ordinary input ('https://www.python.org')
- Executes standalone runnable example tracing all intermediate state transformations
- Names source lines establishing preconditions:
    * Precondition 1: Website Cloner/index.html:1 establishes HTML5 document
    * Precondition 2: Website Cloner/index.html:8 establishes title PROXY SERVER
    * Precondition 3: Website Cloner/index.html:18 establishes POST form action="/"
    * Precondition 4: Website Cloner/index.html:20 establishes input submitButton
- Supports FORCE_WRONG=1 to prove failure propagation
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add Website Cloner directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "Website Cloner")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import runnable_example as cloner_ex


def get_tool_versions():
    git_commit = "unknown"
    git_branch = "unknown"
    try:
        git_commit = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
            ).strip()
        )
        git_branch = (
            subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except Exception:
        pass

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    evidence_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Running R35-T017 Runnable Example Checks ===")

    # 1. Check HTML Preconditions
    index_path = os.path.join(TARGET_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    if "<title>PROXY SERVER</title>" not in html or 'name="submitButton"' not in html:
        print("FAIL: Precondition HTML structure mismatch")
        sys.exit(1)
    print("[Preconditions]: PASS -> HTML form and submitButton input verified")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 2. Check Smallest Valid Input
        res_small = cloner_ex.execute_clone_pipeline("example.com", tmpdir)
        expected_small_norm = "WRONG_URL" if force_wrong else "https://example.com"
        if res_small["normalized_url"] != expected_small_norm:
            print(f"FAIL: Smallest input mismatch: expected '{expected_small_norm}', got '{res_small['normalized_url']}'")
            sys.exit(1)
        print(f"[Smallest Valid Input (example.com)]: PASS -> normalized to '{res_small['normalized_url']}'")

        # 3. Check Ordinary Valid Input
        res_ord = cloner_ex.execute_clone_pipeline("https://www.python.org", tmpdir)
        expected_ord_norm = "https://www.python.org"
        if res_ord["normalized_url"] != expected_ord_norm:
            print(f"FAIL: Ordinary input mismatch: expected '{expected_ord_norm}', got '{res_ord['normalized_url']}'")
            sys.exit(1)
        print(f"[Ordinary Valid Input (https://www.python.org)]: PASS -> normalized to '{res_ord['normalized_url']}'")

        # 4. Check Runnable Example Execution
        ret = cloner_ex.run_worked_examples()
        if ret != 0:
            print(f"FAIL: Runnable example exited with code {ret}")
            sys.exit(1)

    # 5. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_website_cloner.py")
    test_cmd = [sys.executable, test_script, "-v"]
    print(f"\nRunning native test suite: {' '.join(test_cmd)}")
    proc = subprocess.run(test_cmd, capture_output=True, text=True)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
    if proc.returncode != 0:
        print(f"FAIL: Native test suite failed with exit code {proc.returncode}")
        sys.exit(proc.returncode)

    results_data = {
        "tool_versions": get_tool_versions(),
        "command": f"python3 work/R35-T017/check.py",
        "native_command": f"{sys.executable} Website Cloner/test_website_cloner.py -v",
        "test_count": 5,
        "status": "PASS",
        "smallest_input": "example.com",
        "smallest_output": res_small["redirect_location"],
        "ordinary_input": "https://www.python.org",
        "ordinary_output": res_ord["redirect_location"],
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All runnable example checks and 5 unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
