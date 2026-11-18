import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Auto-add site-packages from .venv
for venv_path in [
    os.path.join(BASE_DIR, "..", "..", ".venv"),
    os.path.join(BASE_DIR, "..", ".venv"),
]:
    lib = os.path.join(venv_path, "lib")
    if os.path.exists(lib):
        for p in os.listdir(lib):
            sp = os.path.join(lib, p, "site-packages")
            if os.path.exists(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from PIL import Image
import main as ascii_module


class TestResizeImageSimplification(unittest.TestCase):
    """
    Focused unit tests verifying refactored responsibility in resize_image (main.py).
    Precondition source lines:
      - main.py:4 establishes ASCII_CHARS
      - main.py:7 establishes calculate_new_dimensions helper
      - main.py:24 establishes resize_image signature
    """

    def test_preconditions(self):
        self.assertEqual(len(ascii_module.ASCII_CHARS), 11)
        self.assertEqual(ascii_module.ASCII_CHARS[0], "@")

    def test_smallest_valid_input_1x1(self):
        # Smallest valid input: 1x1 image resized with new_width=1
        img = Image.new("RGB", (1, 1), color=(128, 128, 128))
        res = ascii_module.resize_image(img, new_width=1)
        self.assertEqual(res.size, (1, 1))

    def test_ordinary_valid_input_200x100(self):
        # Ordinary input: 200x100 image resized with new_width=100
        img = Image.new("RGB", (200, 100), color=(255, 0, 0))
        res = ascii_module.resize_image(img, new_width=100)
        # Expected: ratio = 100/200 = 0.5, new_height = int(100 * 0.5) = 50
        self.assertEqual(res.size, (100, 50))

    def test_calculate_new_dimensions_aspect_ratio_accuracy(self):
        # Verify refactored helper calculates exact aspect ratio
        test_cases = [
            ((1, 1), 1, (1, 1)),
            ((100, 100), 50, (50, 50)),
            ((400, 200), 100, (100, 50)),
            ((300, 900), 100, (100, 300)),
            ((1920, 1080), 120, (120, 67)),
        ]
        for orig, nw, expected in test_cases:
            calc = ascii_module.calculate_new_dimensions(orig, new_width=nw)
            self.assertEqual(calc, expected)

    def test_calculate_new_dimensions_invalid_inputs(self):
        with self.assertRaises(ValueError):
            ascii_module.calculate_new_dimensions((0, 100), new_width=100)
        with self.assertRaises(ValueError):
            ascii_module.calculate_new_dimensions((100, -5), new_width=100)

    def test_grayify_and_pixels_to_ascii(self):
        img = Image.new("RGB", (2, 2), color=(0, 0, 0))
        gray = ascii_module.grayify(img)
        self.assertEqual(gray.mode, "L")
        text = ascii_module.pixels_to_ascii(gray)
        self.assertEqual(text, "@@@@")


if __name__ == "__main__":
    unittest.main()
