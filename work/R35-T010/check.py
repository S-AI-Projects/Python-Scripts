"""work/R35-T010/check.py — focused runner for R35-T010 (Recently Accessed Files).

Usage
-----
    python3 work/R35-T010/check.py          # normal run
    FORCE_WRONG=1 python3 work/R35-T010/check.py   # simulate failure (mutant)

Exits 0 on success, non-zero on any failure.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
RESULTS = WORK / "results.json"

sys.path.insert(0, str(ROOT / "Recently Accessed Files"))
import recently_accessed_files as raf  # noqa: E402

# ---------------------------------------------------------------------------
# FORCE_WRONG shim — inject the getmtime mutant.
# ---------------------------------------------------------------------------
FORCE_WRONG = os.environ.get("FORCE_WRONG", "0") == "1"
if FORCE_WRONG:
    import os as _os
    _orig_getatime = _os.path.getatime

    def _mutant_get_file_access_time(file_path):
        """Plausible one-line mutant: getmtime instead of getatime."""
        return _os.path.getmtime(file_path)

    raf.get_file_access_time = _mutant_get_file_access_time

# ---------------------------------------------------------------------------
# Run pytest.
# ---------------------------------------------------------------------------
test_file = str(ROOT / "Recently Accessed Files" / "test_recently_accessed_files.py")
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
# Native checks.
# ---------------------------------------------------------------------------
errors = []

def nc(label, ok):
    s = "PASS" if ok else "FAIL"
    if not ok:
        errors.append(label)
    print(f"  [{s}] {label}")
    return s

print("\n--- Native checks ---")

# Smallest input: getatime=1000.0, getmtime=2000.0 → expect 1000.0
with patch("recently_accessed_files.os.path.getatime", return_value=1000.0), \
     patch("recently_accessed_files.os.path.getmtime", return_value=2000.0):
    r_small = raf.get_file_access_time("")
r1 = nc("smallest ('') → returns getatime 1000.0 (not getmtime 2000.0)", r_small == 1000.0)

# Ordinary input: getatime=5000.0, getmtime=9999.0 → expect 5000.0
with patch("recently_accessed_files.os.path.getatime", return_value=5000.0), \
     patch("recently_accessed_files.os.path.getmtime", return_value=9999.0):
    r_ord = raf.get_file_access_time("/home/user/document.txt")
r2 = nc("ordinary → returns getatime 5000.0 (not getmtime 9999.0)", r_ord == 5000.0)

# getctime mutant check
with patch("recently_accessed_files.os.path.getatime", return_value=1000.0), \
     patch("recently_accessed_files.os.path.getctime", return_value=3000.0):
    r_ctime = raf.get_file_access_time("")
r3 = nc("atime not ctime: returns 1000.0 (not getctime 3000.0)", r_ctime == 1000.0)

native_ok = not errors
overall_ok = (pytest_exit == 0) and native_ok

# ---------------------------------------------------------------------------
# Save results.json.
# ---------------------------------------------------------------------------
import importlib.metadata as _im
try:
    pv = _im.version("pytest")
except Exception:
    pv = "unknown"

results = {
    "task": "R35-T010",
    "tool_versions": {"python": sys.version.split()[0], "pytest": pv},
    "command": " ".join(cmd),
    "pytest_exit_code": pytest_exit,
    "elapsed_seconds": elapsed,
    "mutation": {
        "plausible_mutant": "os.path.getmtime instead of os.path.getatime",
        "distinguishing_input": {"file_path": "", "getatime": 1000.0, "getmtime": 2000.0},
        "original_result": 1000.0,
        "mutant_result": 2000.0,
        "protected_condition": "return os.path.getatime(file_path)  # line 4",
    },
    "native_checks": {"smallest": r1, "ordinary": r2, "atime_not_ctime": r3},
    "errors": errors,
    "overall": "PASS" if overall_ok else "FAIL",
    "force_wrong_active": FORCE_WRONG,
}
RESULTS.write_text(json.dumps(results, indent=2))
print(f"\nResults saved to {RESULTS}")
print(f"\nOverall: {'PASS' if overall_ok else 'FAIL'}")

if not overall_ok:
    if errors:
        print("Errors:", errors)
    sys.exit(1)
