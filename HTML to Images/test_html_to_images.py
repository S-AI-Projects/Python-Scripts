import io
import os
import runpy
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


DEFAULT_SCRIPT_PATH = Path(__file__).resolve().parent / "html-to-images.py"
SCRIPT_PATH = Path(os.environ.get("HTML_TO_IMAGES_SCRIPT", DEFAULT_SCRIPT_PATH))


class TestHtmlToImages(unittest.TestCase):
    def run_script(self, html, background, image_name):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        html_path = Path(temp_dir.name) / "input.html"
        html_path.write_text(html, encoding="utf-8")
        original_html = html_path.read_text(encoding="utf-8")

        screenshot = Mock()
        html_to_image = Mock()
        html_to_image.screenshot = screenshot
        html2image_module = types.ModuleType("html2image")
        html2image_module.Html2Image = Mock(return_value=html_to_image)

        with patch.dict(sys.modules, {"html2image": html2image_module}), \
                patch("builtins.input",
                      side_effect=[str(html_path), image_name, background]), \
                redirect_stdout(io.StringIO()):
            runpy.run_path(str(SCRIPT_PATH), run_name="html_to_images_test")

        self.assertEqual(html_path.read_text(encoding="utf-8"), original_html)
        return screenshot

    def test_smallest_html_with_empty_background_omits_css_argument(self):
        """Lines 5-8 establish the HTML path and the empty-background branch."""
        html = "<p>x</p>"
        expected_call = ((html,), {"save_as": "small.png"})

        screenshot = self.run_script(html, "", "small.png")

        self.assertEqual(screenshot.call_count, 1)
        self.assertEqual(screenshot.call_args, expected_call)

    def test_ordinary_html_passes_background_css(self):
        """Lines 5-11 establish the file input and CSS branch for nonempty background."""
        html = "<html><body><h1>Hello</h1></body></html>"
        background = "lightblue"
        expected_css = "body {background: lightblue;}"
        expected_call = ((html,), {
            "css_str": expected_css,
            "save_as": "hello.png",
        })

        screenshot = self.run_script(html, background, "hello.png")

        self.assertEqual(screenshot.call_count, 1)
        self.assertEqual(screenshot.call_args, expected_call)


if __name__ == "__main__":
    unittest.main()
