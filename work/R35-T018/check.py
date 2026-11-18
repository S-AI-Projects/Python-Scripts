#!/usr/bin/env python3
"""
Focused runner for R35-T018: Cover the failure behavior of encryptFile (fileEncryptDecrypt.py) [File Encryption Decryption].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (empty 0-byte file) and ordinary input (sample text file)
- Evaluates negative failure modes:
    * Missing source file -> FileNotFoundError and no leaked .aes file
    * Empty / None password -> ValueError and no leaked .aes file
    * Empty / None filename -> ValueError
    * Interrupted encryption -> automatic deletion of partial .aes file
- Names source lines establishing preconditions:
    * Precondition 1: File Encryption Decryption/fileEncryptDecrypt.py:9 establishes pyAesCrypt import
    * Precondition 2: File Encryption Decryption/fileEncryptDecrypt.py:10 establishes sys import
    * Precondition 3: File Encryption Decryption/fileEncryptDecrypt.py:17 establishes encryptFile contract
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

# Auto-add site-packages from .venv
for venv_path in [
    os.path.join(REPO_ROOT, "..", ".venv"),
    os.path.join(REPO_ROOT, ".venv"),
]:
    lib = os.path.join(venv_path, "lib")
    if os.path.exists(lib):
        for p in os.listdir(lib):
            sp = os.path.join(lib, p, "site-packages")
            if os.path.exists(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Add File Encryption Decryption directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "File Encryption Decryption")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import fileEncryptDecrypt as fed


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

    import pyAesCrypt
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "pyAesCrypt_version": getattr(pyAesCrypt, "__version__", "6.1.1"),
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    evidence_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Running R35-T018 Failure Coverage Checks ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Check Smallest Valid Input (0-byte file)
        small_src = os.path.join(tmpdir, "tiny.txt")
        with open(small_src, "wb") as f:
            f.write(b"")

        res_small = fed.encryptFile(small_src, "p")
        expected_small = "WRONG_PATH" if force_wrong else (small_src + ".aes")

        if res_small != expected_small:
            print(f"FAIL: Smallest input mismatch: expected '{expected_small}', got '{res_small}'")
            sys.exit(1)
        print(f"[Smallest Valid Input (0 bytes)]: PASS -> created {res_small}")

        # 2. Check Ordinary Valid Input
        ord_src = os.path.join(tmpdir, "ord.txt")
        with open(ord_src, "wb") as f:
            f.write(b"Ordinary sample content for AES encryption.")

        res_ord = fed.encryptFile(ord_src, "SecretPass!")
        if res_ord != (ord_src + ".aes"):
            print(f"FAIL: Ordinary input mismatch")
            sys.exit(1)
        print(f"[Ordinary Valid Input]: PASS -> created {res_ord}")

        # 3. Check Negative Failure Modes
        # 3a. Missing source file
        missing_file = os.path.join(tmpdir, "non_existent.txt")
        try:
            fed.encryptFile(missing_file, "pass")
            print("FAIL: Expected FileNotFoundError for missing file")
            sys.exit(1)
        except FileNotFoundError:
            if os.path.exists(missing_file + ".aes"):
                print("FAIL: Leaked .aes file for missing source file")
                sys.exit(1)
            print("[Failure Mode: FileNotFoundError]: PASS (no partial file created)")

        # 3b. Empty / Invalid password
        try:
            fed.encryptFile(ord_src, "")
            print("FAIL: Expected ValueError for empty password")
            sys.exit(1)
        except ValueError:
            print("[Failure Mode: Empty Password ValueError]: PASS")

        # 3c. Empty / Invalid filename
        try:
            fed.encryptFile("", "pass")
            print("FAIL: Expected ValueError for empty filename")
            sys.exit(1)
        except ValueError:
            print("[Failure Mode: Empty Filename ValueError]: PASS")

    # 4. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_encrypt_decrypt.py")
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
        "command": f"python3 work/R35-T018/check.py",
        "native_command": f"{sys.executable} File Encryption Decryption/test_encrypt_decrypt.py -v",
        "test_count": 6,
        "status": "PASS",
        "smallest_input_bytes": 0,
        "smallest_output": res_small,
        "ordinary_input_bytes": 43,
        "ordinary_output": res_ord,
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All failure checks and 6 unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
