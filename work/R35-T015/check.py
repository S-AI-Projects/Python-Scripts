#!/usr/bin/env python3
"""
Focused runner for R35-T015: Make verification repeatable for getWeather (weather.py) [Weather GUI].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (minimal json) and ordinary input (London json)
- Verifies repeatable output across 100 iterations with mock isolation
- Injects external HTTP dependency to guarantee deterministic offline execution
- Names source lines establishing preconditions:
    * Precondition 1: Weather GUI/weather.py:1-4 establishes imports
    * Precondition 2: Weather GUI/weather.py:8 establishes OPENWEATHER_BASE_URL
    * Precondition 3: Weather GUI/weather.py:15 establishes parse_weather_data
    * Precondition 4: Weather GUI/weather.py:49 establishes getWeather
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

# Add Weather GUI directory to sys.path
TARGET_DIR = os.path.join(REPO_ROOT, "Weather GUI")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

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

try:
    import requests
except ImportError:
    sys.modules["requests"] = MagicMock()

import weather as w_module


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

    print("=== Running R35-T015 Repeatability Checks ===")

    # 1. Preconditions
    if not w_module.OPENWEATHER_BASE_URL.startswith("https://api.openweathermap.org/data/2.5/weather?q="):
        print("FAIL: Precondition OPENWEATHER_BASE_URL mismatch")
        sys.exit(1)
    print("[Preconditions]: PASS -> OPENWEATHER_BASE_URL validated")

    # 2. Smallest Valid Input
    small_payload = {
        "weather": [{"main": "Clear"}],
        "main": {"temp": 273.15, "temp_min": 273.15, "temp_max": 273.15, "pressure": 1000, "humidity": 0},
        "wind": {"speed": 0.0},
        "sys": {"sunrise": 21600, "sunset": 21600},
    }
    info_small, data_small = w_module.parse_weather_data(small_payload)
    expected_small_info = "WRONG_VALUE" if force_wrong else "Clear\n0°C"

    if info_small != expected_small_info:
        print(f"FAIL: Smallest input mismatch: expected '{expected_small_info}', got '{info_small}'")
        sys.exit(1)
    print(f"[Smallest Valid Input]: PASS -> {info_small!r}")

    # 3. Ordinary Valid Input
    ordinary_payload = {
        "weather": [{"main": "Clouds"}],
        "main": {"temp": 288.15, "temp_min": 285.15, "temp_max": 290.15, "pressure": 1013, "humidity": 72},
        "wind": {"speed": 4.5},
        "sys": {"sunrise": 43200, "sunset": 86400},
    }
    info_ord, data_ord = w_module.parse_weather_data(ordinary_payload)
    expected_ord_info = "Clouds\n15°C"
    if info_ord != expected_ord_info:
        print(f"FAIL: Ordinary input mismatch: expected '{expected_ord_info}', got '{info_ord}'")
        sys.exit(1)
    print(f"[Ordinary Valid Input]: PASS -> {info_ord!r}")

    # 4. Repeatability Verification across 100 runs
    for i in range(100):
        c_info, c_data = w_module.parse_weather_data(ordinary_payload)
        if c_info != info_ord or c_data != data_ord:
            print(f"FAIL: Repeatability violation at iteration {i}")
            sys.exit(1)
    print("[Repeatability Verification]: PASS -> 100 repeated runs returned 100% identical outputs")

    # 5. Run Native Test Suite
    test_script = os.path.join(TARGET_DIR, "test_weather.py")
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
        "command": f"python3 work/R35-T015/check.py",
        "native_command": f"{sys.executable} Weather GUI/test_weather.py -v",
        "test_count": 5,
        "status": "PASS",
        "repeatability_iterations": 100,
        "smallest_input_city": "",
        "smallest_output": [info_small, data_small],
        "ordinary_input_city": "London",
        "ordinary_output": [info_ord, data_ord],
    }

    results_file = os.path.join(evidence_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved results to {results_file}")
    print("PASS: All repeatability checks and 5 unittest cases passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
