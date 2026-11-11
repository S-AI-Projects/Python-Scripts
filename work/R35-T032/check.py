#!/usr/bin/env python3
import os
import sys
import tempfile
import glob as glob_module

# Ensure site-packages from .venv is loaded if PIL not globally present
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
TARGET_DIR = os.path.join(ROOT_DIR, "PNG To JPG")
sys.path.insert(0, TARGET_DIR)

import main as png2jpg


def run_checks():
    print("Running boundary regression checks for R35-T032: PNG To JPG...")
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Check 1: Smallest valid input (1x1 pixel PNG)
        # Preconditions established at PNG To JPG/main.py lines 7-23
        tiny_png = os.path.join(tmpdir, "tiny.png")
        Image.new("RGBA", (1, 1), color=(255, 0, 0, 128)).save(tiny_png, "PNG")

        out_tiny = png2jpg.convert_png_to_jpg(tiny_png, quality=95)
        expected_size = (99, 99) if force_wrong else (1, 1)

        with Image.open(out_tiny) as img:
            print(f"[Smallest input 1x1] size: {img.size}, mode: {img.mode}, format: {img.format}")
            if img.size != expected_size:
                print(f"FAIL: Expected size {expected_size}, got {img.size}")
                sys.exit(1)
            if img.mode != "RGB":
                print(f"FAIL: Expected mode 'RGB', got '{img.mode}'")
                sys.exit(1)
            if img.format != "JPEG":
                print(f"FAIL: Expected format 'JPEG', got '{img.format}'")
                sys.exit(1)

        # Check 2: Ordinary input (100x100 pixel PNG)
        ord_png = os.path.join(tmpdir, "ordinary.png")
        Image.new("RGB", (100, 100), color=(10, 20, 30)).save(ord_png, "PNG")
        out_ord = png2jpg.convert_png_to_jpg(ord_png, quality=95)
        with Image.open(out_ord) as img:
            print(f"[Ordinary input 100x100] size: {img.size}, format: {img.format}")
            if img.size != (100, 100):
                print(f"FAIL: Expected size (100, 100), got {img.size}")
                sys.exit(1)

        # Check 3: Valid boundary limits for quality parameter (1 and 100)
        q1_out = png2jpg.convert_png_to_jpg(tiny_png, quality=1)
        q100_out = png2jpg.convert_png_to_jpg(tiny_png, quality=100)
        assert os.path.exists(q1_out) and os.path.exists(q100_out), "Quality boundary files not created"
        print("[Quality boundaries 1 and 100]: PASS")

        # Check 4: Unsupported boundary - Non-existent file
        non_existent = os.path.join(tmpdir, "does_not_exist.png")
        try:
            png2jpg.convert_png_to_jpg(non_existent)
            print("FAIL: Expected FileNotFoundError for non-existent file")
            sys.exit(1)
        except FileNotFoundError:
            print("[Unsupported: FileNotFoundError]: PASS")

        # Check 5: Unsupported quality (< 1 or > 100)
        for bad_q in (0, 101):
            try:
                png2jpg.convert_png_to_jpg(tiny_png, quality=bad_q)
                print(f"FAIL: Expected ValueError for quality={bad_q}")
                sys.exit(1)
            except ValueError:
                pass
        print("[Unsupported: Quality ValueError]: PASS")

    # Run unittest suite in PNG To JPG directory
    import unittest
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All boundary checks passed (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
