import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


MODULE_PATH = Path(__file__).resolve().parent / "main.py"
SPEC = importlib.util.spec_from_file_location("png_to_jpg", MODULE_PATH)
png_to_jpg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(png_to_jpg)


class TestPngToJpgBoundaries(unittest.TestCase):
    def test_smallest_valid_input_1x1_rgba(self):
        """A 1x1 RGBA PNG is accepted; source contract lines 10-13 open, convert, and save it."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "tiny.png"
            output = Path(temp_dir) / "tiny.jpg"
            Image.new("RGBA", (1, 1), (255, 0, 0, 128)).save(source, "PNG")

            returned = png_to_jpg.convert_png_to_jpg(str(source))

            expected_return = str(output)
            expected_size = (1, 1)
            expected_mode = "RGB"
            expected_format = "JPEG"

            self.assertEqual(returned, expected_return)
            self.assertTrue(output.exists())
            with Image.open(output) as converted:
                self.assertEqual(converted.size, expected_size)
                self.assertEqual(converted.mode, expected_mode)
                self.assertEqual(converted.format, expected_format)

    def test_ordinary_input_100x100_rgb(self):
        """A 100x100 RGB PNG is accepted; source contract lines 10-13 open, convert, and save it."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "ordinary.png"
            output = Path(temp_dir) / "ordinary.jpg"
            Image.new("RGB", (100, 100), (10, 20, 30)).save(source, "PNG")

            returned = png_to_jpg.convert_png_to_jpg(str(source))

            expected_return = str(output)
            expected_size = (100, 100)
            expected_mode = "RGB"
            expected_format = "JPEG"

            self.assertEqual(returned, expected_return)
            self.assertTrue(output.exists())
            with Image.open(output) as converted:
                self.assertEqual(converted.size, expected_size)
                self.assertEqual(converted.mode, expected_mode)
                self.assertEqual(converted.format, expected_format)


if __name__ == "__main__":
    unittest.main()
