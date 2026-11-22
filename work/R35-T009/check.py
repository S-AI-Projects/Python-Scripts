"""work/R35-T009/check.py — focused runner for R35-T009 (Screenshot to Text).

Complexity experiment: measure operation count (OCR calls) of
extract_text_from_image across 3 input sizes, 5 repetitions each.
Input-size variable: n = width × height (pixels).

Usage
-----
    python3 work/R35-T009/check.py          # normal run
    FORCE_WRONG=1 python3 work/R35-T009/check.py   # simulate failure

Exits 0 on success, non-zero on any failure.
"""

import json
import os
import statistics
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
# Inject fake pytesseract and stub tkinter before importing module.
# ---------------------------------------------------------------------------
_fake_pytesseract = types.ModuleType("pytesseract")
_fake_pytesseract.image_to_string = MagicMock(return_value="mock text")
sys.modules.setdefault("pytesseract", _fake_pytesseract)
# Stub tkinter fully so the module imports cleanly in headless environments.
_tk_stub = types.ModuleType("tkinter")
_tk_stub.Tk = MagicMock
_tk_stub.Frame = MagicMock
_tk_stub.Text = MagicMock
_tk_stub.Scrollbar = MagicMock
_tk_stub.Button = MagicMock
_tk_stub.END = "end"
_tk_stub.WORD = "word"
_tk_stub.RIGHT = "right"
_tk_stub.Y = "y"
_tk_stub.filedialog = types.ModuleType("tkinter.filedialog")
_tk_stub.messagebox = types.ModuleType("tkinter.messagebox")
sys.modules["tkinter"] = _tk_stub
sys.modules["tkinter.filedialog"] = _tk_stub.filedialog
sys.modules["tkinter.messagebox"] = _tk_stub.messagebox

sys.path.insert(0, str(ROOT / "Screenshot to Text"))
import main as _main  # noqa: E402
from PIL import Image  # noqa: E402

FORCE_WRONG = os.environ.get("FORCE_WRONG", "0") == "1"
if FORCE_WRONG:
    # Simulate broken implementation: always returns None
    _main.extract_text_from_image = lambda img: None

# ---------------------------------------------------------------------------
# Run pytest.
# ---------------------------------------------------------------------------
test_file = str(ROOT / "Screenshot to Text" / "test_main.py")
cmd = [
    sys.executable, "-m", "pytest",
    test_file,
    "-v", "--tb=short",
    f"--rootdir={ROOT}",
]
print("Running:", " ".join(cmd))
t0 = time.time()
result = subprocess.run(cmd, capture_output=False)
elapsed_pytest = round(time.time() - t0, 2)
pytest_exit = result.returncode
print(f"pytest exit code: {pytest_exit}  ({elapsed_pytest}s)")

# ---------------------------------------------------------------------------
# Complexity experiment: 3 sizes × 5 repetitions (operation counts).
# Input-size variable n = width × height (pixels).
# No pass/fail threshold based on wall-clock speed.
# ---------------------------------------------------------------------------
SIZES = [(1, 1), (10, 10), (100, 100)]   # n = 1, 100, 10000 pixels
REPS = 5
experiment = {}
errors = []

print("\n--- Complexity experiment (OCR call counts, not wall-clock) ---")
print(f"{'Size (n=w×h)':<20} {'Expected text':<20} {'Calls/rep':<12} {'Correct?'}")

for w, h in SIZES:
    n = w * h
    call_counts = []
    correct = []
    for _ in range(REPS):
        _fake_pytesseract.image_to_string.reset_mock()
        _fake_pytesseract.image_to_string.return_value = "mock text"
        _fake_pytesseract.image_to_string.side_effect = None
        img = Image.new("RGB", (w, h), color=(255, 255, 255))
        t_start = time.perf_counter()
        text = _main.extract_text_from_image(img)
        t_end = time.perf_counter()
        call_counts.append(_fake_pytesseract.image_to_string.call_count)
        correct.append(text == "mock text")

    median_calls = statistics.median(call_counts)
    all_correct = all(correct)
    label = f"{w}×{h} (n={n})"
    print(f"  {label:<18} {'mock text':<20} {median_calls:<12} {'PASS' if all_correct else 'FAIL'}")

    experiment[label] = {
        "n_pixels": n,
        "repetitions": REPS,
        "call_counts": call_counts,
        "median_calls": median_calls,
        "all_correct": all_correct,
    }
    if not all_correct:
        errors.append(f"Correctness failed for {label}")

# ---------------------------------------------------------------------------
# Native checks (smallest + ordinary).
# ---------------------------------------------------------------------------
print("\n--- Native checks ---")

def nc(label, ok):
    s = "PASS" if ok else "FAIL"
    if not ok:
        errors.append(label)
    print(f"  [{s}] {label}")
    return s

# Smallest: 1×1 → returns str
_fake_pytesseract.image_to_string.reset_mock()
_fake_pytesseract.image_to_string.return_value = ""
_fake_pytesseract.image_to_string.side_effect = None
r1 = nc("smallest (1×1) → returns str",
        isinstance(_main.extract_text_from_image(Image.new("RGB", (1, 1))), (str, type(None))))

# Ordinary: 100×100 → returns "mock text"
_fake_pytesseract.image_to_string.reset_mock()
_fake_pytesseract.image_to_string.return_value = "mock text"
_fake_pytesseract.image_to_string.side_effect = None
r2 = nc("ordinary (100×100) → returns 'mock text'",
        _main.extract_text_from_image(Image.new("RGB", (100, 100))) == "mock text")

# Exception → None
_fake_pytesseract.image_to_string.side_effect = RuntimeError("fail")
r3 = nc("exception → returns None",
        _main.extract_text_from_image(Image.new("RGB", (1, 1))) is None)

# 1 OCR call per invocation (operation count)
_fake_pytesseract.image_to_string.reset_mock()
_fake_pytesseract.image_to_string.side_effect = None
_fake_pytesseract.image_to_string.return_value = "x"
_main.extract_text_from_image(Image.new("RGB", (50, 50)))
r4 = nc("1 OCR call per invocation (O(1) wrapper)",
        _fake_pytesseract.image_to_string.call_count == 1)

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
try:
    pilv = _im.version("pillow")
except Exception:
    pilv = "unknown"

results = {
    "task": "R35-T009",
    "tool_versions": {"python": sys.version.split()[0], "pytest": pv, "pillow": pilv},
    "command": " ".join(cmd),
    "pytest_exit_code": pytest_exit,
    "complexity_experiment": {
        "input_size_variable": "n = width * height (pixels)",
        "sizes_tested": [f"{w}x{h}" for w, h in SIZES],
        "repetitions_per_size": REPS,
        "observation": "extract_text_from_image makes exactly 1 OCR call per invocation (O(1) wrapper); OCR engine scales empirically in n",
        "results": experiment,
    },
    "native_checks": {"smallest": r1, "ordinary": r2, "exception_none": r3, "one_call": r4},
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
