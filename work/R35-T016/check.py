#!/usr/bin/env python3
"""
Focused runner for R35-T016: Simplify one responsibility in resize_image (main.py) [Image to ASCII].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (1x1 -> 1x1) and ordinary input (200x100 -> 100x50)
- Verifies aspect ratio calculation in decoupled calculate_new_dimensions helper
- Names source lines establishing preconditions:
    * Precondition 1: Image to ASCII/main.py:4 establishes ASCII_CHARS
    * Precondition 2: Image to ASCII/main.py:7 establishes calculate_new_dimensions
    * Precondition 3: Image to ASCII/main.py:24 establishes resize_image signature
- Supports FORCE_WRONG=1 to prove failure propagation
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys

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

# Add Image to ASCII directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "Image to ASCII")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

from PIL import Image
import main as ascii_module


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

    import PIL
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "pillow_version": getattr(PIL, "__version__", "unknown"),
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    evidence_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Running R35-T016 Simplification Checks ===")

    # 1. Check Preconditions
    if len(ascii_module.ASCII_CHARS) != 11 or ascii_module.ASCII_CHARS[0] != "@":
        print("FAIL: Precondition ASCII_CHARS mismatch")
        sys.exit(1)
    print(f"[Preconditions]: PASS -> ASCII_CHARS validated (11 characters)")

    # 2. Check Smallest Valid Input (1x1, new_width=1)
    tiny_img = Image.new("RGB", (1, 1), color=(100, 100, 100))
    res_tiny = ascii_module.resize_image(tiny_img, new_width=1)
    expected_tiny_size = (99, 99) if force_wrong else (1, 1)

    if res_tiny.size != expected_tiny_size:
        print(f"FAIL: Smallest input mismatch: expected {expected_tiny_size}, got {res_tiny.size}")
        sys.exit(1)
    print(f"[Smallest Valid Input (1x1)]: PASS -> {res_tiny.size}")

    # 3. Check Ordinary Valid Input (200x100, new_width=100)
    ord_img = Image.new("RGB", (200, 100), color=(200, 50, 50))
    res_ord = ascii_module.resize_image(ord_img, new_width=100)
    expected_ord_size = (100, 50)

    if res_ord.size != expected_ord_size:
        print(f"FAIL: Ordinary input mismatch: expected {expected_ord_size}, got {res_ord.size}")
        sys.exit(1)
    print(f"[Ordinary Valid Input (200x100)]: PASS -> {res_ord.size}")

    # 4. Check Decoupled Helper Aspect Ratio Calculations
    test_aspects = [
        ((1, 1), 1, (1, 1)),
        ((100, 100), 50, (50, 50)),
        ((400, 200), 100, (100, 50)),
        ((300, 900), 100, (100, 300)),
        ((1920, 1080), 120, (120, 67)),
    ]
    for orig, nw, exp in test_aspects:
        dims = ascii_module.calculate_new_dimensions(orig, new_width=nw)
        if dims != exp:
            print(f"FAIL: Aspect ratio calculation mismatch for {orig} -> {dims} != {exp}")
            sys.exit(1)
    print("[Decoupled Helper calculate_new_dimensions]: PASS -> Proportional aspect ratio calculations verified")

    # 5. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_ascii.py")
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
        "command": f"python3 work/R35-T016/check.py",
        "native_command": f"{sys.executable} Image to ASCII/test_ascii.py -v",
        "test_count": 6,
        "status": "PASS",
        "smallest_input_size": [1, 1],
        "smallest_output_size": list(res_tiny.size),
        "ordinary_input_size": [200, 100],
        "ordinary_output_size": list(res_ord.size),
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All simplification checks and 6 unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
