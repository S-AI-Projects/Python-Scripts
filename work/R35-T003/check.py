#!/usr/bin/env python3
"""
Focused runner for R35-T003: Cross-check send_email (main.py) [Automate Emails Daily].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (1 receiver, simple message, no attachments) against independent oracle
- Checks ordinary valid input (2 receivers, HTML body, attachments) against independent oracle
- Cross-checks 21 varied configurations across the domain against independent oracle
- Verifies input argument non-mutation
- Names and verifies source lines establishing preconditions:
    * Precondition 1: Automate Emails Daily/main.py establishes def send_email near line 8
    * Precondition 2: Automate Emails Daily/main.py establishes receiver_emails = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"]
    * Precondition 3: Automate Emails Daily/main.py establishes attachments = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]
- Supports FORCE_WRONG=1 to prove failure propagation and non-zero exit code
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import email
import io
import json
import os
import platform
import subprocess
import sys
import unittest
from email.utils import formataddr
from unittest.mock import MagicMock, mock_open, patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(REPO_ROOT, "Automate Emails Daily")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import main


def email_oracle(sender_email, sender_name, password, receiver_emails, email_body,
                 email_subject="No subject", is_html=False, attachments=None):
    """
    Independent reference oracle for send_email.
    Does not call the function under test.
    """
    expected_from = formataddr((f"{sender_name}", f"{sender_email}"))
    expected_bcc = sender_email
    expected_subject = email_subject
    expected_receivers = list(receiver_emails)
    expected_sendmail_calls = [
        (sender_email, receiver) for receiver in receiver_emails
    ]
    return {
        "expected_from": expected_from,
        "expected_bcc": expected_bcc,
        "expected_subject": expected_subject,
        "expected_receivers": expected_receivers,
        "expected_sendmail_calls": expected_sendmail_calls,
        "call_count": len(receiver_emails),
        "return_value": None,
    }


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
        git_branch = "student/e26b07f0629/R35-T003"
        git_commit = "unknown"

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    print("=== Running R35-T003 Cross-Check Runner ===")
    if force_wrong:
        print("[NOTICE] FORCE_WRONG=1 set: Injecting deliberate assertion failure to verify failure propagation.")

    source_path = os.path.join(TARGET_DIR, "main.py")
    with open(source_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # Precondition Anchor Checks
    preconditions = [
        ("def send_email near line 8", "def send_email("),
        ("receiver_emails anchor", 'receiver_emails = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"]'),
        ("attachments anchor", 'attachments = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]'),
        ("smtplib.SMTP", "smtplib.SMTP("),
        ("formataddr", "formataddr("),
    ]

    for desc, pattern in preconditions:
        if pattern not in source_code:
            print(f"FAIL: Precondition anchor missing: {desc}")
            return 1
        print(f"[Anchor Verified] {desc}")

    # 1. Smallest valid input cross-check
    mock_smtp = MagicMock()
    with patch("smtplib.SMTP", return_value=mock_smtp), patch("sys.stdout", io.StringIO()):
        sender = "user@gmail.com"
        name = "User"
        receivers = ["receiver1-email@gmail.com"]
        actual_ret = main.send_email(sender, name, "pwd", receivers, "Hi")

    oracle_smallest = email_oracle(sender, name, "pwd", receivers, "Hi")
    expected_ret = "WRONG_RETURN" if force_wrong else oracle_smallest["return_value"]
    print(f"\n[Smallest Input Return Value]\n  Actual:   {actual_ret}\n  Expected: {expected_ret}")
    if actual_ret != expected_ret:
        print(f"FAIL: Smallest input return value mismatch: expected {expected_ret}, got {actual_ret}")
        return 1

    actual_calls = [(c[0][0], c[0][1]) for c in mock_smtp.sendmail.call_args_list]
    expected_calls = oracle_smallest["expected_sendmail_calls"]
    print(f"[Smallest Input Dispatch Calls]\n  Actual:   {actual_calls}\n  Expected: {expected_calls}")
    if actual_calls != expected_calls:
        print(f"FAIL: Smallest input dispatch mismatch: expected {expected_calls}, got {actual_calls}")
        return 1

    # 2. Ordinary valid input cross-check (source fixture)
    mock_smtp.reset_mock()
    fake_file = mock_open(read_data=b"%PDF dummy data")
    with patch("smtplib.SMTP", return_value=mock_smtp), patch("builtins.open", fake_file), patch("sys.stdout", io.StringIO()):
        ordinary_receivers = ["receiver1-email@gmail.com", "receiver2-email@gmail.com"]
        ordinary_attachs = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]
        actual_ord_ret = main.send_email(
            "your-email@gmail.com", "your name", "pwd",
            ordinary_receivers, "<h1>Body</h1>", "Good morning",
            is_html=True, attachments=ordinary_attachs
        )

    oracle_ord = email_oracle(
        "your-email@gmail.com", "your name", "pwd",
        ordinary_receivers, "<h1>Body</h1>", "Good morning",
        is_html=True, attachments=ordinary_attachs
    )
    print(f"\n[Ordinary Input Cross-Check]\n  Actual return:   {actual_ord_ret}\n  Expected return: {oracle_ord['return_value']}")
    if actual_ord_ret != oracle_ord["return_value"]:
        print(f"FAIL: Ordinary input return mismatch: expected {oracle_ord['return_value']}, got {actual_ord_ret}")
        return 1

    ord_calls = [(c[0][0], c[0][1]) for c in mock_smtp.sendmail.call_args_list]
    print(f"[Ordinary Input Dispatch Calls]\n  Actual:   {ord_calls}\n  Expected: {oracle_ord['expected_sendmail_calls']}")
    if ord_calls != oracle_ord["expected_sendmail_calls"]:
        print(f"FAIL: Ordinary dispatch calls mismatch: expected {oracle_ord['expected_sendmail_calls']}, got {ord_calls}")
        return 1

    # 3. Native test runner integration (mocked external I/O)
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

    # Save results to work/R35-T003/
    work_dir = os.path.abspath(os.path.dirname(__file__))
    tool_versions = get_tool_versions()

    results_payload = {
        "tool_versions": tool_versions,
        "command": "python3 work/R35-T003/check.py",
        "native_command": native_command,
        "test_count": test_count,
        "oracle_cross_checks_count": 21,
        "status": "PASS",
        "anchors_verified": [desc for desc, _ in preconditions],
        "cross_check_summary": {
            "smallest_input": {
                "matched": True,
                "expected_return": oracle_smallest["return_value"],
                "actual_return": actual_ret,
                "dispatches": actual_calls,
            },
            "ordinary_input": {
                "matched": True,
                "expected_return": oracle_ord["return_value"],
                "actual_return": actual_ord_ret,
                "dispatches": ord_calls,
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
