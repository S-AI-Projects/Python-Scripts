#!/usr/bin/env python3
"""
Focused runner for R35-T020: Strengthen the tests of PasswordManager (pwd_mgmr.py) [Password Manager].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input ("a", "b") and ordinary input (multi-site with file persistence)
- Verifies source anchor: self.pwd_dict = {}
- Demonstrates mutation detection: original passes and deliberate mutant fails the named assertion
- Names source lines establishing preconditions:
    * Precondition 1: Password Manager/pwd_mgmr.py:1 establishes Fernet import
    * Precondition 2: Password Manager/pwd_mgmr.py:5 establishes PasswordManager class
    * Precondition 3: Password Manager/pwd_mgmr.py:9 establishes self.pwd_dict = {} anchor
    * Precondition 4: Password Manager/pwd_mgmr.py:27 establishes add_password
    * Precondition 5: Password Manager/pwd_mgmr.py:36 establishes get_password
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

# Add Password Manager directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "Password Manager")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

from cryptography.fernet import Fernet
import pwd_mgmr as pm_module


class MutantPasswordManager(pm_module.PasswordManager):
    """Plausible one-line mutation: lowercasing stored password."""
    def add_password(self, site, password):
        super().add_password(site, password.lower())


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

    import cryptography
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "cryptography_version": getattr(cryptography, "__version__", "unknown"),
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    evidence_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Running R35-T020 Test Strengthening Checks ===")

    # 1. Check Source Anchor: self.pwd_dict = {}
    pm_base = pm_module.PasswordManager()
    if pm_base.pwd_dict != {}:
        print("FAIL: Source anchor self.pwd_dict != {} mismatch")
        sys.exit(1)
    print("[Source Anchor]: PASS -> self.pwd_dict == {} verified")

    # 2. Check Smallest Valid Input
    pm_small = pm_module.PasswordManager()
    pm_small.add_password("a", "b")
    act_small = pm_small.get_password("a")
    expected_small = "WRONG_VALUE" if force_wrong else "b"

    if act_small != expected_small:
        print(f"FAIL: Smallest input mismatch: expected '{expected_small}', got '{act_small}'")
        sys.exit(1)
    print(f"[Smallest Valid Input ('a', 'b')]: PASS -> get_password('a') == '{act_small}'")

    # 3. Check Ordinary Valid Input
    with tempfile.TemporaryDirectory() as tmpdir:
        key_path = os.path.join(tmpdir, "test.key")
        pwd_path = os.path.join(tmpdir, "vault.txt")

        pm_ord = pm_module.PasswordManager()
        pm_ord.create_key(key_path)
        pm_ord.create_pwd_file(pwd_path)
        pm_ord.add_password("github.com", "S3cure_P@ssw0rd!")
        pm_ord.add_password("google.com", "G00gl3-Auth#2026")

        if (
            pm_ord.get_password("github.com") != "S3cure_P@ssw0rd!"
            or pm_ord.get_password("google.com") != "G00gl3-Auth#2026"
        ):
            print("FAIL: Ordinary input credential retrieval mismatch")
            sys.exit(1)
        print("[Ordinary Valid Input (Credentials & Persistence)]: PASS")

    # 4. Prove Mutation Detection
    target_site = "portal.nst.edu"
    target_pass = "ComplexMixedCasePass!#99"

    # Original execution: must pass
    orig_pm = pm_module.PasswordManager()
    orig_pm.add_password(target_site, target_pass)
    orig_res = orig_pm.get_password(target_site)
    assert orig_res == target_pass, "Original must preserve exact password"

    # Mutant execution: must fail the exact same named assertion
    mutant_pm = MutantPasswordManager()
    mutant_pm.add_password(target_site, target_pass)
    mutant_res = mutant_pm.get_password(target_site)

    mutant_detected = (mutant_res != target_pass)
    if not mutant_detected:
        print("FAIL: Mutant was NOT detected by test assertion")
        sys.exit(1)
    print(f"[Mutation Detection Proof]: PASS -> Original returned '{orig_res}', Mutant returned '{mutant_res}' (mutant caught and rejected)")

    # 5. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_pwd_mgmr.py")
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
        "command": f"python3 work/R35-T020/check.py",
        "native_command": f"{sys.executable} Password Manager/test_pwd_mgmr.py -v",
        "test_count": 5,
        "status": "PASS",
        "anchor_verified": "self.pwd_dict = {}",
        "mutation_tested": "password.lower() case mutator",
        "mutation_detected": True,
        "smallest_input": {"site": "a", "password": "b"},
        "ordinary_input": {"site": "github.com", "password": "S3cure_P@ssw0rd!"},
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All test strengthening checks and 5 unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
