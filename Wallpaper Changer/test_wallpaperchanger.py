import unittest
import random
import os
import sys
import glob as glob_module

try:
    from PIL import Image
except ImportError:
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import wallpaperchanger as wc


class TestAddMarginInvariant(unittest.TestCase):
    def test_smallest_valid_input(self):
        # Line 57: add_margin(img, top, left, bottom, right, color)
        # Smallest input: 1x1 image, 1px margin all around
        img = Image.new("RGB", (1, 1), color=(100, 150, 200))
        res = wc.add_margin(img, top=1, left=1, bottom=1, right=1, color=(0, 0, 0))

        self.assertEqual(res.size, (3, 3))
        self.assertEqual(res.mode, "RGB")
        # Center pixel (1, 1) must equal original pixel
        self.assertEqual(res.getpixel((1, 1)), (100, 150, 200))
        # Border pixel (0, 0) must equal margin color
        self.assertEqual(res.getpixel((0, 0)), (0, 0, 0))
        # Original input remains unmutated
        self.assertEqual(img.size, (1, 1))

    def test_ordinary_valid_input(self):
        img = Image.new("RGB", (100, 60), color=(50, 60, 70))
        res = wc.add_margin(img, top=10, left=20, bottom=15, right=25, color=(255, 0, 0))

        self.assertEqual(res.size, (145, 85))
        self.assertEqual(res.mode, "RGB")
        sub_crop = res.crop((20, 10, 20 + 100, 10 + 60))
        self.assertEqual(list(sub_crop.getdata()), list(img.getdata()))
        self.assertEqual(img.size, (100, 60))

    def test_100_bounded_property_cases(self):
        rng = random.Random(42)
        for i in range(100):
            w = rng.randint(1, 50)
            h = rng.randint(1, 50)
            top = rng.randint(0, 20)
            left = rng.randint(0, 20)
            bottom = rng.randint(0, 20)
            right = rng.randint(0, 20)
            color = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            mode = rng.choice(["RGB", "L"])
            img_color = color if mode == "RGB" else rng.randint(0, 255)
            margin_color = color if mode == "RGB" else rng.randint(0, 255)

            img = Image.new(mode, (w, h), color=img_color)
            orig_data = list(img.getdata())

            res = wc.add_margin(img, top, left, bottom, right, margin_color)

            # Invariant 1: Dimensions
            self.assertEqual(res.width, w + left + right)
            self.assertEqual(res.height, h + top + bottom)

            # Invariant 2: Mode
            self.assertEqual(res.mode, mode)

            # Invariant 3: Sub-image content
            sub = res.crop((left, top, left + w, top + h))
            self.assertEqual(list(sub.getdata()), orig_data)

            # Invariant 4: Input immutability
            self.assertEqual(img.size, (w, h))
            self.assertEqual(list(img.getdata()), orig_data)


if __name__ == "__main__":
    unittest.main()
