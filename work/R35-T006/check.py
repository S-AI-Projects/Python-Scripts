"""work/R35-T006/check.py — focused runner for R35-T006 (No Screensaver).

Usage
-----
    python3 work/R35-T006/check.py          # normal run
    FORCE_WRONG=1 python3 work/R35-T006/check.py   # simulate failure

Exits 0 on success, non-zero on any failure.
"""

import json
import os
import subprocess
import sys
import time
import types
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
RESULTS = WORK / "results.json"


# ---------------------------------------------------------------------------
# 1. Inject fake pyautogui BEFORE importing the module under test.
# ---------------------------------------------------------------------------
_fake_pyautogui = types.ModuleType("pyautogui")
_fake_pyautogui.sleep = MagicMock()
_fake_pyautogui.click = MagicMock()
sys.modules.setdefault("pyautogui", _fake_pyautogui)

sys.path.insert(0, str(ROOT / "No Screensaver"))
import noscreensaver  # noqa: E402


# ---------------------------------------------------------------------------
# 2. FORCE_WRONG shim — deliberately break keep_awake to test exit-code.
# ---------------------------------------------------------------------------
FORCE_WRONG = os.environ.get("FORCE_WRONG", "0") == "1"
if FORCE_WRONG:
    _orig_keep_awake = noscreensaver.keep_awake

    def _broken_keep_awake(interval_seconds=40, click_x=50, click_y=400):
        _fake_pyautogui.sleep(interval_seconds)
        _fake_pyautogui.click(999, 999)   # wrong co-ordinates

    noscreensaver.keep_awake = _broken_keep_awake


# ---------------------------------------------------------------------------
# 3. Run pytest on the test file.
# ---------------------------------------------------------------------------
test_file = str(ROOT / "No Screensaver" / "test_noscreensaver.py")
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
# 4. Native checks (smallest + ordinary fixture).
# ---------------------------------------------------------------------------
errors = []

def _reset():
    _fake_pyautogui.sleep.reset_mock()
    _fake_pyautogui.click.reset_mock()

def native_check(label, interval, cx, cy, exp_sleep, exp_click):
    _reset()
    noscreensaver.keep_awake(interval_seconds=interval, click_x=cx, click_y=cy)
    actual_sleep = _fake_pyautogui.sleep.call_args
    actual_click = _fake_pyautogui.click.call_args
    ok_sleep = actual_sleep and actual_sleep.args == (exp_sleep,)
    ok_click = actual_click and actual_click.args == exp_click
    status = "PASS" if (ok_sleep and ok_click) else "FAIL"
    if status == "FAIL":
        errors.append(
            f"{label}: sleep={actual_sleep} click={actual_click} "
            f"(expected sleep({exp_sleep}), click{exp_click})"
        )
    print(f"  [{status}] {label}")
    return status

print("\n--- Native checks ---")
r1 = native_check("smallest (1,0,0)", 1, 0, 0, 1, (0, 0))
r2 = native_check("ordinary (40,50,400)", 40, 50, 400, 40, (50, 400))
r3 = native_check("defaults", 40, 50, 400, 40, (50, 400))

native_ok = not errors
overall_ok = (pytest_exit == 0) and native_ok

# ---------------------------------------------------------------------------
# 5. Save results.json.
# ---------------------------------------------------------------------------
import importlib.metadata as _im
try:
    pyautogui_ver = _im.version("pyautogui")
except Exception:
    pyautogui_ver = "not-installed"

try:
    pytest_ver = _im.version("pytest")
except Exception:
    pytest_ver = "unknown"

results = {
    "task": "R35-T006",
    "tool_versions": {
        "python": sys.version.split()[0],
        "pytest": pytest_ver,
        "pyautogui": pyautogui_ver,
    },
    "command": " ".join(cmd),
    "pytest_exit_code": pytest_exit,
    "elapsed_seconds": elapsed,
    "native_checks": {
        "smallest_input": r1,
        "ordinary_input": r2,
        "defaults_match": r3,
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
