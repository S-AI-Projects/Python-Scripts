#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import MagicMock

# Mock faker before importing FakeProfile to enable testing without external I/O
if "faker" not in sys.modules:
    mock_faker_mod = MagicMock()
    mock_fake_instance = MagicMock()
    mock_fake_instance.locales = ['it_IT', 'en_US', 'ja_JP']
    mock_fake_instance.name.return_value = "Jane Doe"
    mock_fake_instance.email.return_value = "janedoe@example.com"
    mock_fake_instance.ssn.return_value = "987-65-4321"
    mock_fake_instance.address.return_value = "456 Market St, San Francisco, CA"
    mock_fake_instance.latitude.return_value = 37.789
    mock_fake_instance.longitude.return_value = -122.401
    mock_fake_instance.url.return_value = "https://janedoe.org"
    mock_faker_mod.Faker.return_value = mock_fake_instance
    sys.modules["faker"] = mock_faker_mod

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Fake Profile")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import FakeProfile as fp


def run_checks():
    print("Running focused boundary checks for R35-T042: generate_fake_profiles...")

    # Anchor checks & verification
    # Source fixture anchor: profiles = []
    source_file = os.path.join(TARGET_DIR, "FakeProfile.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "profiles = []" in source_code, (
        "Precondition anchor missing: profiles = []"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid boundary input (num_profiles = 1)
    res_smallest = fp.generate_fake_profiles(1)
    expected_len = 999 if force_wrong else 1

    print(f"[Smallest input 1] Profile count: {len(res_smallest)}, Expected: {expected_len}")
    if len(res_smallest) != expected_len:
        print(f"FAIL: Expected profile count {expected_len}, got {len(res_smallest)}")
        sys.exit(1)
    if res_smallest[0]["Name"] != "Jane Doe":
        print(f"FAIL: Expected profile name 'Jane Doe', got '{res_smallest[0]['Name']}'")
        sys.exit(1)

    # Check 2: Valid interior ordinary input (num_profiles = 3)
    res_ordinary = fp.generate_fake_profiles(3)
    print(f"[Ordinary input 3] Profile count: {len(res_ordinary)}, Expected: 3")
    if len(res_ordinary) != 3:
        print(f"FAIL: Expected profile count 3, got {len(res_ordinary)}")
        sys.exit(1)

    # Check 3: Unsupported boundary value zero (num_profiles = 0)
    try:
        fp.generate_fake_profiles(0)
        print("FAIL: Expected ValueError for num_profiles = 0")
        sys.exit(1)
    except ValueError as e:
        print(f"[Boundary 0 (Unsupported)] Caught expected ValueError: {e}")

    # Check 4: Unsupported boundary negative value (num_profiles = -1)
    try:
        fp.generate_fake_profiles(-1)
        print("FAIL: Expected ValueError for num_profiles = -1")
        sys.exit(1)
    except ValueError as e:
        print(f"[Boundary -1 (Unsupported)] Caught expected ValueError: {e}")

    # Run unittest suite in Fake Profile directory
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All boundary checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
