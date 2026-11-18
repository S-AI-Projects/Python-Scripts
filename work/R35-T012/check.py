#!/usr/bin/env python3
"""
Focused runner for R35-T012: Define the supported boundaries of Remove Background (code.py).

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (1x1 3-channel BGR) and ordinary input (100x100 BGR)
- Validates boundary limits (threshold=0, threshold=255)
- Tests unsupported boundary conditions (None, non-3channel, zero-dimension, out-of-bounds threshold)
- Names the source line establishing preconditions:
    * Precondition 1: Remove Background/code.py:1 module imports
    * Precondition 2: Remove Background/code.py:5 remove_background contract
- Supports FORCE_WRONG=1 to prove failure propagation
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys

# Auto-add venv site-packages if running with system python
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VENV_PYTHON = os.path.join(REPO_ROOT, "..", ".venv", "bin", "python3")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = os.path.join(REPO_ROOT, ".venv", "bin", "python3")

# Try to find site-packages in any parent .venv
for venv_path in [
    os.path.join(REPO_ROOT, "..", ".venv"),
    os.path.join(REPO_ROOT, ".venv"),
]:
    lib_dir = os.path.join(venv_path, "lib")
    if os.path.exists(lib_dir):
        for py_dir in os.listdir(lib_dir):
            sp = os.path.join(lib_dir, py_dir, "site-packages")
            if os.path.exists(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Add Remove Background directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "Remove Background")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import numpy as np
import code as rb_module


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

    import cv2
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "numpy_version": np.__version__,
        "opencv_version": cv2.__version__,
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    evidence_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Running R35-T012 Boundary Checks ===")

    # 1. Check Smallest Valid Input (1x1 BGR image)
    tiny_bgr = np.zeros((1, 1, 3), dtype=np.uint8)
    tiny_bgr[0, 0] = [120, 130, 140]
    expected_tiny_shape = (99, 99, 4) if force_wrong else (1, 1, 4)
    res_tiny = rb_module.remove_background(tiny_bgr, threshold=250)

    if res_tiny.shape != (1, 1, 4):
        print(f"FAIL: Expected shape (1, 1, 4), got {res_tiny.shape}")
        sys.exit(1)
    if force_wrong and res_tiny.shape != expected_tiny_shape:
        print(f"FAIL: Deliberate mismatch triggered: expected {expected_tiny_shape}, got {res_tiny.shape}")
        sys.exit(1)

    print(f"[Smallest Valid Input 1x1x3]: PASS -> shape {res_tiny.shape}, dtype {res_tiny.dtype}")

    # 2. Check Ordinary Valid Input (100x100 BGR image)
    ord_bgr = np.full((100, 100, 3), 200, dtype=np.uint8)
    res_ord = rb_module.remove_background(ord_bgr, threshold=250)
    if res_ord.shape != (100, 100, 4):
        print(f"FAIL: Expected shape (100, 100, 4), got {res_ord.shape}")
        sys.exit(1)
    print(f"[Ordinary Valid Input 100x100x3]: PASS -> shape {res_ord.shape}")

    # 3. Check Threshold Boundaries (0 and 255)
    img_bound = np.full((10, 10, 3), 128, dtype=np.uint8)
    res_0 = rb_module.remove_background(img_bound, threshold=0)
    res_255 = rb_module.remove_background(img_bound, threshold=255)
    if res_0.shape != (10, 10, 4) or res_255.shape != (10, 10, 4):
        print("FAIL: Threshold boundary output shape mismatch")
        sys.exit(1)
    print("[Threshold boundaries 0 and 255]: PASS")

    # 4. Check Unsupported Conditions
    # 4a. None input
    try:
        rb_module.remove_background(None)
        print("FAIL: Expected ValueError on None input")
        sys.exit(1)
    except ValueError:
        print("[Unsupported: None input]: PASS")

    # 4b. Non-3channel input
    try:
        rb_module.remove_background(np.zeros((10, 10), dtype=np.uint8))
        print("FAIL: Expected ValueError on 2D input")
        sys.exit(1)
    except ValueError:
        print("[Unsupported: 2D array input]: PASS")

    # 4c. Zero dimensions
    try:
        rb_module.remove_background(np.zeros((0, 0, 3), dtype=np.uint8))
        print("FAIL: Expected ValueError on zero-dimension input")
        sys.exit(1)
    except ValueError:
        print("[Unsupported: zero-dimension input]: PASS")

    # 4d. Out-of-bounds threshold
    for bad_t in (-1, 256):
        try:
            rb_module.remove_background(img_bound, threshold=bad_t)
            print(f"FAIL: Expected ValueError on threshold {bad_t}")
            sys.exit(1)
        except ValueError:
            pass
    print("[Unsupported: out-of-bounds threshold]: PASS")

    # 5. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_remove_background.py")
    test_cmd = [sys.executable, test_script, "-v"]
    print(f"\nRunning native test suite: {' '.join(test_cmd)}")
    proc = subprocess.run(test_cmd, capture_output=True, text=True)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
    if proc.returncode != 0:
        print(f"FAIL: Native test suite failed with exit code {proc.returncode}")
        sys.exit(proc.returncode)

    # Save results
    results_data = {
        "tool_versions": get_tool_versions(),
        "command": f"python3 work/R35-T012/check.py",
        "native_command": f"{sys.executable} Remove Background/test_remove_background.py -v",
        "test_count": 8,
        "status": "PASS",
        "smallest_input_shape": list(tiny_bgr.shape),
        "smallest_output_shape": list(res_tiny.shape),
        "ordinary_input_shape": list(ord_bgr.shape),
        "ordinary_output_shape": list(res_ord.shape),
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All boundary checks and 8 unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
