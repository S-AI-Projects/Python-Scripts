#!/usr/bin/env python3
import os
import sys
import unittest
import random
import glob as glob_module

# Ensure PIL is available
try:
    from PIL import Image
except ImportError:
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Wallpaper Changer")
sys.path.insert(0, TARGET_DIR)

import wallpaperchanger as wc


def run_checks():
    print("Running invariant property checks for R35-T034: add_margin...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Smallest input: 1x1 image, margins (1, 1, 1, 1)
    img_tiny = Image.new("RGB", (1, 1), color=(100, 150, 200))
    res_tiny = wc.add_margin(img_tiny, top=1, left=1, bottom=1, right=1, color=(0, 0, 0))
    expected_tiny_size = (99, 99) if force_wrong else (3, 3)

    print(f"[Smallest input 1x1] Expected size: {expected_tiny_size}, Got size: {res_tiny.size}")
    if res_tiny.size != expected_tiny_size:
        print(f"FAIL: Invariant broken: size {res_tiny.size} != {expected_tiny_size}")
        sys.exit(1)
    assert res_tiny.mode == "RGB", "Mode invariant violated"
    assert res_tiny.getpixel((1, 1)) == (100, 150, 200), "Sub-image identity invariant violated"
    assert res_tiny.getpixel((0, 0)) == (0, 0, 0), "Margin color invariant violated"
    assert img_tiny.size == (1, 1), "Input immutability invariant violated"

    # Ordinary input: 100x60 image, margins (10, 20, 15, 25)
    img_ord = Image.new("RGB", (100, 60), color=(50, 60, 70))
    res_ord = wc.add_margin(img_ord, top=10, left=20, bottom=15, right=25, color=(255, 0, 0))
    expected_ord_size = (145, 85)
    print(f"[Ordinary input 100x60] Expected size: {expected_ord_size}, Got size: {res_ord.size}")
    if res_ord.size != expected_ord_size:
        print(f"FAIL: Invariant broken: size {res_ord.size} != {expected_ord_size}")
        sys.exit(1)
    sub = res_ord.crop((20, 10, 20 + 100, 10 + 60))
    assert list(sub.getdata()) == list(img_ord.getdata()), "Sub-image pixel invariant violated"

    # 100 bounded property cases
    rng = random.Random(42)
    for i in range(100):
        w = rng.randint(1, 40)
        h = rng.randint(1, 40)
        top = rng.randint(0, 15)
        left = rng.randint(0, 15)
        bottom = rng.randint(0, 15)
        right = rng.randint(0, 15)
        color = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
        img = Image.new("RGB", (w, h), color=color)
        orig_data = list(img.getdata())

        res = wc.add_margin(img, top, left, bottom, right, color)
        assert res.size == (w + left + right, h + top + bottom), f"Case #{i} size invariant broken"
        assert res.mode == img.mode, f"Case #{i} mode invariant broken"
        assert list(res.crop((left, top, left + w, top + h)).getdata()) == orig_data, f"Case #{i} data invariant broken"
        assert img.size == (w, h), f"Case #{i} immutability broken"

    print("[100 Bounded Property Invariant Cases]: PASS")

    # Run unittest suite
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All invariant checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
