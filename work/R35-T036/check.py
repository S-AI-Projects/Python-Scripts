#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import io
import glob as glob_module

# Ensure requests is available
try:
    import requests
except ImportError:
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import requests

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "InstaDownloader")
sys.path.insert(0, TARGET_DIR)

import insta_down


def run_checks():
    print("Running refactoring checks for R35-T036: InstaDownloader connection...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest input (url='http://127.0.0.1', timeout=1)
    # Preconditions established at insta_down.py lines 20-35
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("requests.get", return_value=mock_resp):
        with patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            res_small = insta_down.connection(url="http://127.0.0.1", timeout=1)
            output_small = fake_out.getvalue()
        expected_small = False if force_wrong else True
        print(f"[Smallest input] Expected: {expected_small}, Got: {res_small}")
        if res_small != expected_small:
            print(f"FAIL: Expected {expected_small}, got {res_small}")
            sys.exit(1)
        assert "You're connected to internet" in output_small

    # Check 2: Ordinary input (url='http://www.google.com/', timeout=5)
    with patch("requests.get", return_value=mock_resp):
        with patch("sys.stdout", new_callable=io.StringIO):
            res_ord = insta_down.connection(url="http://www.google.com/", timeout=5)
        print(f"[Ordinary input] Expected: True, Got: {res_ord}")
        if not res_ord:
            print("FAIL: Expected True for ordinary successful connection")
            sys.exit(1)

    # Check 3: Error classifications through extracted sub-responsibility
    with patch("requests.get", side_effect=requests.ConnectionError()):
        c_status, c_msg = insta_down.check_url_reachability("http://unreachable.local", 1)
        assert c_status is False
        assert "No internet connection available" in c_msg
    print("[Extracted reachability error classification]: PASS")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All refactoring checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
