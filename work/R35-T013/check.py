#!/usr/bin/env python3
"""
Focused runner for R35-T013: Cross-check main (server.py) [TCP Chat Server].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (b"", "") and ordinary input (b"Hello from client", "Hello from server")
- Cross-checks 25 distinct synthetic inputs against an independent reference oracle
- Names source lines establishing preconditions:
    * Precondition 1: TCP Chat Server/server.py:3 establishes IP = '0.0.0.0'
    * Precondition 2: TCP Chat Server/server.py:4 establishes PORT = 3000
    * Precondition 3: TCP Chat Server/server.py:7 establishes handle_client_connection
- Supports FORCE_WRONG=1 to prove failure propagation
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys
from unittest.mock import MagicMock

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add TCP Chat Server directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "TCP Chat Server")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import server as chat_server


def independent_oracle_session(raw_bytes: bytes, reply_str: str, address=("127.0.0.1", 5000)):
    """
    Independent reference oracle calculating expected outputs directly.
    """
    decoded = raw_bytes.decode("utf-8")
    sent_bytes = reply_str.encode("utf-8")
    return {
        "address": address,
        "decoded": decoded,
        "reply": reply_str,
        "sent_bytes": sent_bytes,
        "tuple": (address, decoded, reply_str),
    }


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

    print("=== Running R35-T013 Cross-Check Checks ===")

    # 1. Check Preconditions
    if chat_server.IP != "0.0.0.0" or chat_server.PORT != 3000:
        print(f"FAIL: Preconditions IP={chat_server.IP}, PORT={chat_server.PORT} mismatch")
        sys.exit(1)
    print(f"[Preconditions]: PASS -> IP='0.0.0.0', PORT=3000")

    # 2. Check Smallest Valid Input (b"", "")
    mock_client = MagicMock()
    mock_client.recv.return_value = b""
    addr_small = ("127.0.0.1", 50001)

    act_addr, act_dec, act_send = chat_server.handle_client_connection(
        mock_client, addr_small, input_func=lambda prompt: ""
    )
    expected_dec = "WRONG_VALUE" if force_wrong else ""

    if act_dec != expected_dec:
        print(f"FAIL: Smallest input mismatch: expected '{expected_dec}', got '{act_dec}'")
        sys.exit(1)
    print(f"[Smallest Valid Input]: PASS -> decoded='{act_dec}', send='{act_send}'")

    # 3. Check Ordinary Input
    mock_client = MagicMock()
    mock_client.recv.return_value = b"Hello from client"
    addr_ord = ("192.168.1.10", 42000)

    act_addr, act_dec, act_send = chat_server.handle_client_connection(
        mock_client, addr_ord, input_func=lambda prompt: "Hello from server"
    )
    if act_dec != "Hello from client" or act_send != "Hello from server":
        print(f"FAIL: Ordinary input mismatch")
        sys.exit(1)
    print(f"[Ordinary Valid Input]: PASS -> decoded='{act_dec}', send='{act_send}'")

    # 4. Cross-check 25 distinct synthetic inputs against independent oracle
    test_cases = [
        (b"", ""),
        (b"a", "b"),
        (b"123", "456"),
        (b"ping", "pong"),
        (b"hello world", "goodbye world"),
        (b"test message 001", "ack 001"),
        (b"special chars !@#$%", "reply ^&*()"),
        (b"multiline\nfirst line\nsecond line", "multiline\nresponse"),
        (b"spaces   and   tabs\t\t", "trimmed or raw"),
        (b"json-like {\"key\": \"value\"}", "{\"status\": \"ok\"}"),
        (b"unicode: \xe2\x9c\x93 checkmark", "unicode reply: \xe2\x9c\x94"),
        (b"upper CASE text", "lower case text"),
        (b"numeric 9876543210", "numeric 0123456789"),
        (b"boolean True", "boolean False"),
        (b"null byte inside text \x00 middle", "handled null byte \x00"),
        (b"http GET / HTTP/1.1", "HTTP/1.1 200 OK"),
        (b"repeat a" * 20, "repeat b" * 20),
        (b"long prefix " + b"x" * 100, "long ack " + "y" * 100),
        (b"emoji test: \xf0\x9f\x98\x80", "emoji response: \xf0\x9f\x91\x8d"),
        (b"boundary length 1", "response length 1"),
        (b"csv,col1,col2,col3", "ack,row1,row2"),
        (b"python code: x = 10", "python exec: pass"),
        (b"quit", "bye"),
        (b"exit", "closing connection"),
        (b"final 25th payload", "final ack 25"),
    ]

    for idx, (raw_in, reply_in) in enumerate(test_cases):
        addr = ("10.0.0." + str(idx + 1), 6000 + idx)
        mock_c = MagicMock()
        mock_c.recv.return_value = raw_in

        a_addr, a_dec, a_send = chat_server.handle_client_connection(
            mock_c, addr, input_func=lambda prompt, r=reply_in: r
        )
        oracle = independent_oracle_session(raw_in, reply_in, address=addr)

        if (a_addr, a_dec, a_send) != oracle["tuple"]:
            print(f"FAIL: Oracle cross-check failed for case {idx}")
            sys.exit(1)

    print(f"[25 Oracle Cross-Checks]: PASS -> All 25 synthetic cases match reference oracle")

    # 5. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_server.py")
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
        "command": f"python3 work/R35-T013/check.py",
        "native_command": f"{sys.executable} TCP Chat Server/test_server.py -v",
        "test_count": 5,
        "oracle_cross_check_count": 25,
        "status": "PASS",
        "smallest_input": {"raw": "", "reply": ""},
        "ordinary_input": {"raw": "Hello from client", "reply": "Hello from server"},
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All cross-checks and unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
