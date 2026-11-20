#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure PIL.Image is mocked if not installed
if "PIL" not in sys.modules:
    mock_pil = MagicMock()
    mock_image_module = MagicMock()
    mock_pil.Image = mock_image_module
    sys.modules["PIL"] = mock_pil
    sys.modules["PIL.Image"] = mock_image_module

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Image to GIF")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import imageTogif as itg


def independent_oracle(frame_list, output_name="my_awesome.gif"):
    """Independent reference oracle for make_gif."""
    if not frame_list:
        raise ValueError("No frames")
    return {
        "output_filepath": output_name,
        "format": "GIF",
        "total_frames": len(frame_list),
        "first_frame": frame_list[0],
        "duration": 100,
        "loop": 0,
        "save_all": True,
    }


def run_checks():
    print("Running focused cross-check regression checks for R35-T043: make_gif...")

    # Anchor checks & verification
    # Source fixture anchor: frame_one = frames[0] (line 5)
    source_file = os.path.join(TARGET_DIR, "imageTogif.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "frame_one = frames[0]" in source_code, (
        "Precondition anchor missing: frame_one = frames[0]"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid input (1 frame)
    fake_single = ["/test/folder/img_0.JPG"]
    mock_frame = MagicMock()
    with patch("glob.glob", return_value=fake_single), \
         patch.object(itg.Image, "open", return_value=mock_frame):
        res_single = itg.make_gif("/test/folder")
        expected_out = "WRONG_OUTPUT.gif" if force_wrong else "my_awesome.gif"
        print(f"[Smallest input 1 frame] Result: {res_single}, Expected: {expected_out}")
        if res_single != expected_out:
            print(f"FAIL: Expected {expected_out}, got {res_single}")
            sys.exit(1)

        args, kwargs = mock_frame.save.call_args
        if kwargs.get("format") != "GIF" or kwargs.get("duration") != 100:
            print(f"FAIL: Unexpected save kwargs {kwargs}")
            sys.exit(1)

    # Check 2: Ordinary valid input (5 frames)
    fake_5 = [f"/test/folder/img_{i}.JPG" for i in range(5)]
    mock_frames = [MagicMock() for _ in range(5)]
    with patch("glob.glob", return_value=fake_5), \
         patch.object(itg.Image, "open", side_effect=lambda p: mock_frames[int(p.split('_')[-1].split('.')[0])]):
        res_ord = itg.make_gif("/test/folder", output_filepath="ordinary.gif")
        print(f"[Ordinary input 5 frames] Result: {res_ord}, Expected: ordinary.gif")
        if res_ord != "ordinary.gif":
            print(f"FAIL: Expected ordinary.gif, got {res_ord}")
            sys.exit(1)

    # Check 3: Enumerate 25 inputs against independent oracle
    for count in range(1, 26):
        files = [f"/frames/img_{i}.JPG" for i in range(count)]
        frames = [MagicMock() for _ in range(count)]
        target_name = f"test_{count}.gif"
        oracle_spec = independent_oracle(files, target_name)

        with patch("glob.glob", return_value=files), \
             patch.object(itg.Image, "open", side_effect=lambda p: frames[int(p.split('_')[-1].split('.')[0])]):
            out = itg.make_gif("/frames", output_filepath=target_name)
            if out != oracle_spec["output_filepath"]:
                print(f"FAIL at test #{count}: output mismatch with oracle")
                sys.exit(1)

            args, kwargs = frames[0].save.call_args
            if kwargs["format"] != oracle_spec["format"] or \
               kwargs["duration"] != oracle_spec["duration"] or \
               kwargs["loop"] != oracle_spec["loop"] or \
               kwargs["save_all"] != oracle_spec["save_all"] or \
               len(kwargs["append_images"]) != oracle_spec["total_frames"]:
                print(f"FAIL at test #{count}: save arguments mismatch with oracle")
                sys.exit(1)

    print("[Oracle cross-check across 25 configurations]: PASS")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
