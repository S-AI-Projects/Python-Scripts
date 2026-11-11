import unittest
import os
import sys
import tempfile
import glob as glob_module

# Add site-packages from .venv if PIL is not installed in standard sys.path
try:
    from PIL import Image
except ImportError:
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import main as png2jpg


class TestPngToJpgBoundaries(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_smallest_valid_input_1x1(self):
        # Smallest valid input: 1x1 pixel PNG
        src_path = os.path.join(self.temp_dir.name, "tiny.png")
        img = Image.new("RGBA", (1, 1), color=(255, 0, 0, 128))
        img.save(src_path, "PNG")

        out_path = png2jpg.convert_png_to_jpg(src_path, quality=95)
        self.assertTrue(os.path.exists(out_path))
        with Image.open(out_path) as res:
            self.assertEqual(res.size, (1, 1))
            self.assertEqual(res.mode, "RGB")
            self.assertEqual(res.format, "JPEG")

    def test_ordinary_valid_input_100x100(self):
        # Ordinary valid input: 100x100 pixel PNG
        src_path = os.path.join(self.temp_dir.name, "ordinary.png")
        img = Image.new("RGB", (100, 100), color=(10, 20, 30))
        img.save(src_path, "PNG")

        out_path = png2jpg.convert_png_to_jpg(src_path, quality=95)
        self.assertTrue(os.path.exists(out_path))
        with Image.open(out_path) as res:
            self.assertEqual(res.size, (100, 100))
            self.assertEqual(res.format, "JPEG")

    def test_quality_boundary_valid_limits(self):
        src_path = os.path.join(self.temp_dir.name, "boundary.png")
        img = Image.new("RGB", (10, 10), color=(50, 60, 70))
        img.save(src_path, "PNG")

        # Lower boundary quality=1
        out1 = png2jpg.convert_png_to_jpg(src_path, quality=1)
        self.assertTrue(os.path.exists(out1))

        # Upper boundary quality=100
        out100 = png2jpg.convert_png_to_jpg(src_path, quality=100)
        self.assertTrue(os.path.exists(out100))

    def test_unsupported_nonexistent_file(self):
        # Unsupported: non-existent file
        fake_path = os.path.join(self.temp_dir.name, "nonexistent.png")
        with self.assertRaises(FileNotFoundError):
            png2jpg.convert_png_to_jpg(fake_path)

    def test_unsupported_quality_values(self):
        src_path = os.path.join(self.temp_dir.name, "test_q.png")
        img = Image.new("RGB", (5, 5))
        img.save(src_path, "PNG")

        with self.assertRaises(ValueError):
            png2jpg.convert_png_to_jpg(src_path, quality=0)
        with self.assertRaises(ValueError):
            png2jpg.convert_png_to_jpg(src_path, quality=101)


if __name__ == "__main__":
    unittest.main()
