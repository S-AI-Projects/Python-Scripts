"""work/R35-T007/check.py — focused runner for R35-T007 (Automating Emails).

Usage
-----
    python3 work/R35-T007/check.py          # normal run
    FORCE_WRONG=1 python3 work/R35-T007/check.py   # simulate failure

Exits 0 on success, non-zero on any failure.
"""

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
RESULTS = WORK / "results.json"

# ---------------------------------------------------------------------------
# Load module under test via importlib (filename has a hyphen).
# ---------------------------------------------------------------------------
_src = ROOT / "Automating Emails" / "Birthday-Manager.py"
_spec = importlib.util.spec_from_file_location("Birthday_Manager", _src)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

EmailSender = _mod.EmailSender
BirthdayMessage = _mod.BirthdayMessage


# ---------------------------------------------------------------------------
# Stub — no live SMTP.
# ---------------------------------------------------------------------------
class StubEmailSender(EmailSender):
    def __init__(self):
        self.sent = []

    def send_email(self, recipient, message):
        self.sent.append((recipient, message))


# ---------------------------------------------------------------------------
# FORCE_WRONG shim.
# ---------------------------------------------------------------------------
FORCE_WRONG = os.environ.get("FORCE_WRONG", "0") == "1"
if FORCE_WRONG:
    _orig_send = StubEmailSender.send_email

    def _broken_send(self, recipient, message):
        self.sent.append(("WRONG", "WRONG"))   # corrupted output

    StubEmailSender.send_email = _broken_send


# ---------------------------------------------------------------------------
# Run pytest on the test file.
# ---------------------------------------------------------------------------
test_file = str(ROOT / "Automating Emails" / "test_birthday_manager.py")
cmd = [
    sys.executable, "-m", "pytest",
    test_file,
    "-v", "--tb=short",
    f"--rootdir={ROOT}",
]
print("Running:", " ".join(cmd))
t0 = time.time()
result = subprocess.run(cmd, capture_output=False)
elapsed = round(time.time() - t0, 2)
pytest_exit = result.returncode
print(f"pytest exit code: {pytest_exit}  ({elapsed}s)")

# ---------------------------------------------------------------------------
# Native checks (smallest + ordinary fixture + intermediate state).
# ---------------------------------------------------------------------------
errors = []

def native_check(label, fn, expected, actual):
    ok = actual == expected
    status = "PASS" if ok else "FAIL"
    if not ok:
        errors.append(f"{label}: expected={expected!r}, got={actual!r}")
    print(f"  [{status}] {label}")
    return status

print("\n--- Native checks ---")

# Smallest valid input
s1 = StubEmailSender()
s1.send_email("", "")
r1 = native_check("smallest: sent == [('', '')]", None, [("", "")], s1.sent)

# Ordinary input
s2 = StubEmailSender()
msg = BirthdayMessage.create_message("Alice")
s2.send_email("alice@example.com", msg)
r2 = native_check("ordinary: recipient == 'alice@example.com'", None,
                   "alice@example.com", s2.sent[-1][0])
r3 = native_check("ordinary: 'Happy Birthday' in message", None,
                   True, "Happy Birthday" in s2.sent[-1][1])

# Intermediate state
s3 = StubEmailSender()
s3.send_email("", "")
s3.send_email("alice@example.com", msg)
r4 = native_check("intermediate state: len(sent)==2 after 2 calls", None, 2, len(s3.sent))

native_ok = not errors
overall_ok = (pytest_exit == 0) and native_ok

# ---------------------------------------------------------------------------
# Save results.json.
# ---------------------------------------------------------------------------
import importlib.metadata as _im
try:
    pytest_ver = _im.version("pytest")
except Exception:
    pytest_ver = "unknown"

results = {
    "task": "R35-T007",
    "tool_versions": {
        "python": sys.version.split()[0],
        "pytest": pytest_ver,
    },
    "command": " ".join(cmd),
    "pytest_exit_code": pytest_exit,
    "elapsed_seconds": elapsed,
    "native_checks": {
        "smallest_input": r1,
        "ordinary_recipient": r2,
        "ordinary_message": r3,
        "intermediate_state": r4,
    },
    "errors": errors,
    "overall": "PASS" if overall_ok else "FAIL",
    "force_wrong_active": FORCE_WRONG,
}
RESULTS.write_text(json.dumps(results, indent=2))
print(f"\nResults saved to {RESULTS}")
print(f"\nOverall: {'PASS' if overall_ok else 'FAIL'}")

if not overall_ok:
    if errors:
        print("Native check errors:", errors)
    sys.exit(1)
