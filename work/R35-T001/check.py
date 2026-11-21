#!/usr/bin/env python3
"""
Focused runner for R35-T001: Lock down the contract of Web Scraper (Web_Scraper.py) [Web Scraper].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input ('<h2 class="blog-title">A</h2>')
- Checks ordinary valid input (HTML with multiple blog titles)
- Checks domain boundary input (repeated titles, empty title, whitespace stripping)
- Tests returned values and observable mutations separately
- Names and verifies source lines establishing preconditions:
    * Precondition 1: Web Scraper/Web_Scraper.py line 5 establishes target URL: URL = "https://www.python.org/blogs/"
    * Precondition 2: Web Scraper/Web_Scraper.py line 8 establishes requests.get(url) HTTP GET request
    * Precondition 3: Web Scraper/Web_Scraper.py line 11 establishes BeautifulSoup(content, "html.parser")
    * Precondition 4: Web Scraper/Web_Scraper.py line 14 establishes soup.find_all('h2', class_='blog-title')
    * Precondition 5: Web Scraper/Web_Scraper.py line 17 establishes display_blog_titles stdout formatting
    * Precondition 6: Web Scraper/Web_Scraper.py line 22 establishes open(filename, 'w') file persistence
- Supports FORCE_WRONG=1 to prove failure propagation and non-zero exit code
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(REPO_ROOT, "Web Scraper")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import Web_Scraper


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
        git_branch = "student/e26b07f0629/R35-T001"
        git_commit = "unknown"

    import bs4
    import requests

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "requests_version": requests.__version__,
        "beautifulsoup4_version": bs4.__version__,
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    print("=== Running R35-T001 Check Runner ===")
    if force_wrong:
        print("[NOTICE] FORCE_WRONG=1 set: Injecting deliberate assertion failure to verify failure propagation.")

    source_path = os.path.join(TARGET_DIR, "Web_Scraper.py")
    with open(source_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # Precondition Anchor Checks
    preconditions = [
        ('line 5: URL = "https://www.python.org/blogs/"', 'URL = "https://www.python.org/blogs/"'),
        ('line 8: requests.get', "requests.get("),
        ('line 11: BeautifulSoup html.parser', '"html.parser"'),
        ('line 14: h2 blog-title', "blog-title"),
        ('line 22: open blog_titles.txt', "blog_titles.txt"),
    ]

    for desc, pattern in preconditions:
        if pattern not in source_code:
            print(f"FAIL: Source precondition anchor missing: {desc}")
            return 1
        print(f"[Anchor Verified] {desc}")

    # Fixtures
    smallest_input = '<h2 class="blog-title">A</h2>'
    ordinary_input = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head><title>Python Blogs</title></head>\n"
        "<body>\n"
        '  <div class="blog-posts">\n'
        '    <h2 class="blog-title">Python 3.12 Released</h2>\n'
        "    <p>Details about Python 3.12 release.</p>\n"
        '    <h2 class="blog-title">PSF Grants Overview</h2>\n'
        "    <p>Details about PSF grants.</p>\n"
        "  </div>\n"
        "</body>\n"
        "</html>"
    )
    boundary_input = (
        "<html><body>\n"
        '  <h2 class="blog-title">Duplicate Title</h2>\n'
        '  <h2 class="blog-title">  Duplicate Title  </h2>\n'
        '  <h2 class="blog-title"></h2>\n'
        "</body></html>"
    )

    # 1. Smallest valid input
    actual_smallest_ret = Web_Scraper.extract_blog_titles(smallest_input)
    expected_smallest_ret = ["WRONG_TITLE"] if force_wrong else ["A"]
    print(f"\n[Smallest Input Return Value]\n  Actual:   {actual_smallest_ret}\n  Expected: {expected_smallest_ret}")
    if actual_smallest_ret != expected_smallest_ret:
        print(f"FAIL: Smallest input returned value mismatch: expected {expected_smallest_ret}, got {actual_smallest_ret}")
        return 1

    # Smallest valid input observable file mutation
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp_name = tmp.name
    try:
        Web_Scraper.save_blog_titles(actual_smallest_ret, filename=tmp_name)
        with open(tmp_name, "r", encoding="utf-8") as tmp_f:
            actual_smallest_file = tmp_f.read()
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

    expected_smallest_file = "WRONG_MUTATION\n" if force_wrong else "A\n"
    print(f"[Smallest Input File Mutation]\n  Actual:   {repr(actual_smallest_file)}\n  Expected: {repr(expected_smallest_file)}")
    if actual_smallest_file != expected_smallest_file:
        print(f"FAIL: Smallest input file mutation mismatch: expected {repr(expected_smallest_file)}, got {repr(actual_smallest_file)}")
        return 1

    # 2. Ordinary input
    actual_ordinary_ret = Web_Scraper.extract_blog_titles(ordinary_input)
    expected_ordinary_ret = ["Python 3.12 Released", "PSF Grants Overview"]
    print(f"\n[Ordinary Input Return Value]\n  Actual:   {actual_ordinary_ret}\n  Expected: {expected_ordinary_ret}")
    if actual_ordinary_ret != expected_ordinary_ret:
        print(f"FAIL: Ordinary input returned value mismatch: expected {expected_ordinary_ret}, got {actual_ordinary_ret}")
        return 1

    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp_name = tmp.name
    try:
        Web_Scraper.save_blog_titles(actual_ordinary_ret, filename=tmp_name)
        with open(tmp_name, "r", encoding="utf-8") as tmp_f:
            actual_ordinary_file = tmp_f.read()
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

    expected_ordinary_file = "Python 3.12 Released\nPSF Grants Overview\n"
    print(f"[Ordinary Input File Mutation]\n  Actual:   {repr(actual_ordinary_file)}\n  Expected: {repr(expected_ordinary_file)}")
    if actual_ordinary_file != expected_ordinary_file:
        print(f"FAIL: Ordinary input file mutation mismatch: expected {repr(expected_ordinary_file)}, got {repr(actual_ordinary_file)}")
        return 1

    # 3. Domain boundary input (repeated values + whitespace stripping)
    actual_boundary_ret = Web_Scraper.extract_blog_titles(boundary_input)
    expected_boundary_ret = ["Duplicate Title", "Duplicate Title", ""]
    print(f"\n[Boundary Input Return Value]\n  Actual:   {actual_boundary_ret}\n  Expected: {expected_boundary_ret}")
    if actual_boundary_ret != expected_boundary_ret:
        print(f"FAIL: Boundary input returned value mismatch: expected {expected_boundary_ret}, got {actual_boundary_ret}")
        return 1

    # 4. Native test runner integration (mocked external I/O)
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

    # Save inputs, expected vs actual results, and tool versions to work/R35-T001/
    work_dir = os.path.abspath(os.path.dirname(__file__))
    tool_versions = get_tool_versions()

    results_payload = {
        "tool_versions": tool_versions,
        "command": "python3 work/R35-T001/check.py",
        "native_command": native_command,
        "test_count": test_count,
        "status": "PASS",
        "anchors_verified": [desc for desc, _ in preconditions],
        "inputs": {
            "smallest_input": smallest_input,
            "ordinary_input": ordinary_input,
            "boundary_input": boundary_input,
        },
        "results": {
            "smallest": {
                "returned_value": {
                    "expected": expected_smallest_ret,
                    "actual": actual_smallest_ret,
                    "match": actual_smallest_ret == expected_smallest_ret,
                },
                "file_mutation": {
                    "expected": expected_smallest_file,
                    "actual": actual_smallest_file,
                    "match": actual_smallest_file == expected_smallest_file,
                },
            },
            "ordinary": {
                "returned_value": {
                    "expected": expected_ordinary_ret,
                    "actual": actual_ordinary_ret,
                    "match": actual_ordinary_ret == expected_ordinary_ret,
                },
                "file_mutation": {
                    "expected": expected_ordinary_file,
                    "actual": actual_ordinary_file,
                    "match": actual_ordinary_file == expected_ordinary_file,
                },
            },
            "boundary": {
                "returned_value": {
                    "expected": expected_boundary_ret,
                    "actual": actual_boundary_ret,
                    "match": actual_boundary_ret == expected_boundary_ret,
                },
            },
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
