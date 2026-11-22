import importlib.util
import random
import unittest
from pathlib import Path

from PIL import Image


MODULE_PATH = Path(__file__).resolve().parent / "wallpaperchanger.py"
SPEC = importlib.util.spec_from_file_location("wallpaperchanger", MODULE_PATH)
wallpaperchanger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wallpaperchanger)


class TestAddMarginInvariants(unittest.TestCase):
    def test_smallest_valid_input(self):
        """Line 38 defines add_margin; lines 49-53 establish dimensions, mode, and paste position."""
        original = Image.new("RGB", (1, 1), (100, 150, 200))
        original_copy = original.copy()

        result = wallpaperchanger.add_margin(
            original, top=1, left=1, bottom=1, right=1, color=(0, 0, 0)
        )

        expected_size = (3, 3)
        expected_mode = "RGB"
        expected_center = (100, 150, 200)
        expected_margin = (0, 0, 0)

        self.assertEqual(result.size, expected_size)
        self.assertEqual(result.mode, expected_mode)
        self.assertEqual(result.getpixel((1, 1)), expected_center)
        self.assertEqual(result.getpixel((0, 0)), expected_margin)
        for y in range(expected_size[1]):
            for x in range(expected_size[0]):
                if not (x == 1 and y == 1):
                    self.assertEqual(result.getpixel((x, y)), expected_margin)
        self.assertEqual(original.tobytes(), original_copy.tobytes())
        self.assertEqual(original.size, (1, 1))

    def test_ordinary_valid_input(self):
        """Line 49 establishes the original width and height for 100x60 dimensions."""
        original = Image.new("RGB", (100, 60), (50, 60, 70))
        original_copy = original.copy()

        result = wallpaperchanger.add_margin(
            original, top=10, left=20, bottom=15, right=25, color=(255, 0, 0)
        )

        expected_size = (145, 85)
        expected_mode = "RGB"
        expected_original_position = (20, 10, 120, 70)

        self.assertEqual(result.size, expected_size)
        self.assertEqual(result.mode, expected_mode)
        placed = result.crop(expected_original_position)
        self.assertEqual(placed.tobytes(), original.tobytes())
        self.assertEqual(original.tobytes(), original_copy.tobytes())

        for y in range(result.height):
            for x in range(result.width):
                if not (20 <= x < 120 and 10 <= y < 70):
                    self.assertEqual(result.getpixel((x, y)), (255, 0, 0))

    def test_100_bounded_valid_cases(self):
        """Fixed seed 42 creates 100 valid RGB and grayscale configurations."""
        rng = random.Random(42)

        for case_number in range(100):
            width = rng.randint(1, 50)
            height = rng.randint(1, 50)
            top = rng.randint(0, 20)
            left = rng.randint(0, 20)
            bottom = rng.randint(0, 20)
            right = rng.randint(0, 20)
            mode = rng.choice(("RGB", "L"))

            if mode == "RGB":
                content = tuple(rng.randint(0, 255) for _ in range(3))
                margin = tuple(rng.randint(0, 255) for _ in range(3))
            else:
                content = rng.randint(0, 255)
                margin = rng.randint(0, 255)

            original = Image.new(mode, (width, height), content)
            original_bytes = original.tobytes()

            result = wallpaperchanger.add_margin(
                original, top, left, bottom, right, margin
            )

            expected_width = width + left + right
            expected_height = height + top + bottom
            expected_position = (
                left,
                top,
                left + width,
                top + height,
            )

            with self.subTest(case=case_number):
                self.assertEqual(result.size, (expected_width, expected_height))
                self.assertEqual(result.mode, mode)
                self.assertEqual(
                    result.crop(expected_position).tobytes(),
                    original_bytes,
                )
                self.assertEqual(original.size, (width, height))
                self.assertEqual(original.tobytes(), original_bytes)

                for y in range(expected_height):
                    for x in range(expected_width):
                        if not (left <= x < left + width and
                                top <= y < top + height):
                            self.assertEqual(result.getpixel((x, y)), margin)


if __name__ == "__main__":
    unittest.main()
