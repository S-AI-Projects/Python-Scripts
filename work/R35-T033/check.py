#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch
from collections import namedtuple
import glob as glob_module

# Ensure psutil is available
try:
    import psutil
except ImportError:
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import psutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Hardware Detector")
sys.path.insert(0, TARGET_DIR)

import hardware_detector as hd

VMem = namedtuple("VMem", ["total", "used"])
DiskUsage = namedtuple("DiskUsage", ["free"])


def oracle(total_bytes, used_bytes, free_disk_bytes, cores, usage_pct):
    GIB = 1073741824.0
    return {
        'ram_total_gb': round(total_bytes / GIB, 2),
        'ram_used_gb': round(used_bytes / GIB, 2),
        'available_diskspace_gb': round(free_disk_bytes / GIB, 2),
        'cpu_cores': int(cores),
        'cpu_usage_percent': float(usage_pct),
    }


def run_checks():
    print("Running reference comparison checks for R35-T033: HardwareDetector...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check anchor initialization: line 34 (self.hardware_profile = {})
    detector = hd.HardwareDetector()
    assert detector.hardware_profile == {}, "Anchor self.hardware_profile not initialized to empty dict"

    # Smallest valid input
    with patch("psutil.virtual_memory", return_value=VMem(total=1073741824, used=0)), \
         patch("psutil.disk_usage", return_value=DiskUsage(free=1073741824)), \
         patch("psutil.cpu_count", return_value=1), \
         patch("psutil.cpu_percent", return_value=0.0):
        detector.get_computer_specs()
        expected_smallest = {
            'ram_total_gb': 99.0 if force_wrong else 1.0,
            'ram_used_gb': 0.0,
            'available_diskspace_gb': 1.0,
            'cpu_cores': 1,
            'cpu_usage_percent': 0.0,
        }
        print(f"[Smallest input 1GB/1core] Result: {detector.hardware_profile}")
        if detector.hardware_profile != expected_smallest:
            print(f"FAIL: Expected {expected_smallest}, got {detector.hardware_profile}")
            sys.exit(1)

    # Ordinary valid input
    detector = hd.HardwareDetector()
    with patch("psutil.virtual_memory", return_value=VMem(total=16 * 1073741824, used=8 * 1073741824)), \
         patch("psutil.disk_usage", return_value=DiskUsage(free=100 * 1073741824)), \
         patch("psutil.cpu_count", return_value=8), \
         patch("psutil.cpu_percent", return_value=15.5):
        detector.get_computer_specs()
        expected_ordinary = {
            'ram_total_gb': 16.0,
            'ram_used_gb': 8.0,
            'available_diskspace_gb': 100.0,
            'cpu_cores': 8,
            'cpu_usage_percent': 15.5,
        }
        print(f"[Ordinary input 16GB/8core] Result: {detector.hardware_profile}")
        if detector.hardware_profile != expected_ordinary:
            print(f"FAIL: Expected {expected_ordinary}, got {detector.hardware_profile}")
            sys.exit(1)

    # Enumerate 25 inputs against independent oracle
    for i in range(1, 26):
        total_ram = i * (1024**3)
        used_ram = (i // 2) * (1024**3)
        free_disk = (i * 10) * (1024**3)
        cores = max(1, i % 16)
        usage = float((i * 3.7) % 100)

        with patch("psutil.virtual_memory", return_value=VMem(total=total_ram, used=used_ram)), \
             patch("psutil.disk_usage", return_value=DiskUsage(free=free_disk)), \
             patch("psutil.cpu_count", return_value=cores), \
             patch("psutil.cpu_percent", return_value=usage):
            d = hd.HardwareDetector()
            d.get_computer_specs()
            expected = oracle(total_ram, used_ram, free_disk, cores, usage)
            if d.hardware_profile != expected:
                print(f"FAIL at test #{i}: mismatch with oracle")
                sys.exit(1)
    print("[Oracle cross-check across 25 configurations]: PASS")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
