"""work/R35-T008/check.py — focused runner for R35-T008 (University Rankings).

Usage
-----
    python3 work/R35-T008/check.py          # normal run
    FORCE_WRONG=1 python3 work/R35-T008/check.py   # simulate failure

Exits 0 on success, non-zero on any failure.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch, mock_open
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
RESULTS = WORK / "results.json"

sys.path.insert(0, str(ROOT / "University Rankings"))
import univRanking  # noqa: E402

# ---------------------------------------------------------------------------
# Shared mock DataFrames.
# ---------------------------------------------------------------------------
def _ranking_df():
    return pd.DataFrame({
        "Country": ["USA"],
        "Institution name": ["Washington University"],
        "Score": [100.0],
    })

def _capitals_df():
    return pd.DataFrame({
        "Country Name": ["USA"],
        "Capital": ["Washington"],
        "Continent": ["North America"],
    })

_dfs = {"ranking.csv": _ranking_df(), "capitals.csv": _capitals_df()}

# ---------------------------------------------------------------------------
# FORCE_WRONG shim — suppress ZeroDivisionError so failure check passes wrong.
# ---------------------------------------------------------------------------
FORCE_WRONG = os.environ.get("FORCE_WRONG", "0") == "1"
if FORCE_WRONG:
    _orig = univRanking.getInformation

    def _patched(selectedCountry, rankingFileName, capitalsFileName):
        # Does NOT raise on unknown country — simulates broken failure path
        if selectedCountry == "Unknown":
            return None
        return _orig(selectedCountry, rankingFileName, capitalsFileName)

    univRanking.getInformation = _patched

# ---------------------------------------------------------------------------
# Run pytest.
# ---------------------------------------------------------------------------
test_file = str(ROOT / "University Rankings" / "test_univRanking.py")
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
    status = "PASS" if ok else "FAIL"
    if not ok:
        errors.append(label)
    print(f"  [{status}] {label}")
    return status

print("\n--- Native checks ---")

# Check 1: failure path raises ZeroDivisionError
raised = False
try:
    with patch("univRanking.pd.read_csv", side_effect=lambda f: _dfs[f]), \
         patch("builtins.open", mock_open()):
        univRanking.getInformation("Unknown", "ranking.csv", "capitals.csv")
except ZeroDivisionError:
    raised = True
r1 = nc("failure path: 'Unknown' raises ZeroDivisionError", raised)

# Check 2: ordinary input does NOT raise
ok2 = True
try:
    with patch("univRanking.pd.read_csv", side_effect=lambda f: _dfs[f]), \
         patch("builtins.open", mock_open()):
        univRanking.getInformation("USA", "ranking.csv", "capitals.csv")
except ZeroDivisionError:
    ok2 = False
r2 = nc("ordinary input 'USA' does not raise", ok2)

# Check 3: success after failure
raised2 = False
try:
    with patch("univRanking.pd.read_csv", side_effect=lambda f: _dfs[f]), \
         patch("builtins.open", mock_open()):
        univRanking.getInformation("Unknown", "ranking.csv", "capitals.csv")
except ZeroDivisionError:
    raised2 = True

ok3 = True
try:
    with patch("univRanking.pd.read_csv", side_effect=lambda f: _dfs[f]), \
         patch("builtins.open", mock_open()):
        univRanking.getInformation("USA", "ranking.csv", "capitals.csv")
except ZeroDivisionError:
    ok3 = False
r3 = nc("success after failure: 'USA' works after 'Unknown' fails", raised2 and ok3)

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
try:
    pandas_ver = _im.version("pandas")
except Exception:
    pandas_ver = "unknown"

results = {
    "task": "R35-T008",
    "tool_versions": {
        "python": sys.version.split()[0],
        "pytest": pytest_ver,
        "pandas": pandas_ver,
    },
    "command": " ".join(cmd),
    "pytest_exit_code": pytest_exit,
    "elapsed_seconds": elapsed,
    "native_checks": {
        "failure_path_zero_division": r1,
        "ordinary_usa_success": r2,
        "success_after_failure": r3,
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
