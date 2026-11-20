#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch, call

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "FileRenamer")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import File_Renamer as fr


def run_checks():
    print("Running focused refactoring checks for R35-T046: rename_files...")

    # Anchor checks & verification
    source_file = os.path.join(TARGET_DIR, "File_Renamer.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "def rename_files" in source_code, (
        "Precondition anchor missing: rename_files"
    )
    assert "compute_renamed_filename" in source_code, (
        "Refactored responsibility helper missing: compute_renamed_filename"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid input (1 matching file)
    with patch("os.listdir", return_value=["IMG_001.jpg"]), \
         patch("os.rename") as mock_rename:
        fr.rename_files("/photos", r"IMG.*", "pic_")
        expected_call = call("/photos/IMG_001.jpg", "/photos/WRONG_0.jpg") if force_wrong else call("/photos/IMG_001.jpg", "/photos/pic_0.jpg")

        actual_call = mock_rename.call_args
        print(f"[Smallest input 1 file] Expected rename: {expected_call}, Actual: {actual_call}")
        if actual_call != expected_call:
            print(f"FAIL: Expected {expected_call}, got {actual_call}")
            sys.exit(1)

    # Check 2: Ordinary valid input (3 files, 2 matching)
    with patch("os.listdir", return_value=["IMG_10.png", "notes.txt", "IMG_20.png"]), \
         patch("os.rename") as mock_rename:
        fr.rename_files("/gallery", r"IMG.*", "pic_")
        if mock_rename.call_count != 2:
            print(f"FAIL: Expected 2 rename calls, got {mock_rename.call_count}")
            sys.exit(1)
        mock_rename.assert_has_calls([
            call("/gallery/IMG_10.png", "/gallery/pic_0.png"),
            call("/gallery/IMG_20.png", "/gallery/pic_1.png")
        ])
    print("[Ordinary input 3 files, 2 matching]: PASS")

    # Check 3: Unit test suite execution
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All refactoring checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
