"""Tests for Screenshot to Text/main.py — R35-T009.

Fixture (written BEFORE editing the implementation):
    Smallest valid input : img = Image.new("RGB", (1, 1))   → text="" or "\n"
    Ordinary input       : img = Image.new("RGB", (100, 100)) → text string or ""

Precondition anchor:
    ``def extract_text_from_image(img):``  # line 6

pytesseract is mocked — no tesseract binary required.
"""

import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Inject fake pytesseract before importing the module under test.
# ---------------------------------------------------------------------------
_fake_pytesseract = types.ModuleType("pytesseract")
_fake_pytesseract.image_to_string = MagicMock(return_value="Hello World")
sys.modules.setdefault("pytesseract", _fake_pytesseract)

# Stub tkinter fully so the module imports cleanly in headless environments.
_tk_stub = types.ModuleType("tkinter")
_tk_stub.Tk = MagicMock
_tk_stub.Frame = MagicMock
_tk_stub.Text = MagicMock
_tk_stub.Scrollbar = MagicMock
_tk_stub.Button = MagicMock
_tk_stub.END = "end"
_tk_stub.WORD = "word"
_tk_stub.RIGHT = "right"
_tk_stub.Y = "y"
_tk_stub.filedialog = types.ModuleType("tkinter.filedialog")
_tk_stub.messagebox = types.ModuleType("tkinter.messagebox")
sys.modules["tkinter"] = _tk_stub
sys.modules["tkinter.filedialog"] = _tk_stub.filedialog
sys.modules["tkinter.messagebox"] = _tk_stub.messagebox

sys.path.insert(0, "Screenshot to Text")
import main as _main  # noqa: E402

from PIL import Image  # noqa: E402


def _make_img(width, height):
    """Create a plain white RGB image of given dimensions."""
    return Image.new("RGB", (width, height), color=(255, 255, 255))


# ---------------------------------------------------------------------------
# Tests — smallest valid input (1×1 pixel)
# ---------------------------------------------------------------------------
class TestExtractTextSmallestInput(unittest.TestCase):
    """extract_text_from_image with smallest valid input: 1×1 image."""

    def setUp(self):
        _fake_pytesseract.image_to_string.reset_mock()
        _fake_pytesseract.image_to_string.return_value = ""
        _fake_pytesseract.image_to_string.side_effect = None

    def test_smallest_returns_string(self):
        """Smallest input (1×1) → returns a str (possibly empty)."""
        # Precondition anchor: def extract_text_from_image(img):  # line 6
        # Expected: str
        img = _make_img(1, 1)
        result = _main.extract_text_from_image(img)
        self.assertIsInstance(result, str)

    def test_smallest_calls_pytesseract(self):
        """Smallest input → pytesseract.image_to_string called once."""
        img = _make_img(1, 1)
        _main.extract_text_from_image(img)
        _fake_pytesseract.image_to_string.assert_called_once_with(img)

    def test_smallest_no_mutation(self):
        """Input image is not mutated by extract_text_from_image."""
        img = _make_img(1, 1)
        size_before = img.size
        _main.extract_text_from_image(img)
        self.assertEqual(img.size, size_before)


# ---------------------------------------------------------------------------
# Tests — ordinary input (100×100 image)
# ---------------------------------------------------------------------------
class TestExtractTextOrdinaryInput(unittest.TestCase):
    """extract_text_from_image with ordinary input: 100×100 image."""

    def setUp(self):
        _fake_pytesseract.image_to_string.reset_mock()
        _fake_pytesseract.image_to_string.return_value = "Sample extracted text"
        _fake_pytesseract.image_to_string.side_effect = None

    def test_ordinary_returns_string(self):
        """Ordinary input (100×100) → returns str."""
        # Precondition anchor: def extract_text_from_image(img):  # line 6
        # Expected: "Sample extracted text"
        img = _make_img(100, 100)
        result = _main.extract_text_from_image(img)
        self.assertEqual(result, "Sample extracted text")

    def test_ordinary_calls_pytesseract(self):
        """Ordinary input → pytesseract.image_to_string called once."""
        img = _make_img(100, 100)
        _main.extract_text_from_image(img)
        _fake_pytesseract.image_to_string.assert_called_once_with(img)


# ---------------------------------------------------------------------------
# Tests — exception path: returns None
# ---------------------------------------------------------------------------
class TestExtractTextExceptionPath(unittest.TestCase):
    """extract_text_from_image returns None when pytesseract raises."""

    def setUp(self):
        _fake_pytesseract.image_to_string.reset_mock()
        _fake_pytesseract.image_to_string.side_effect = RuntimeError("OCR failed")

    def test_exception_returns_none(self):
        """When pytesseract raises, extract_text_from_image returns None."""
        # Expected: None
        img = _make_img(1, 1)
        result = _main.extract_text_from_image(img)
        self.assertIsNone(result)

    def test_exception_does_not_propagate(self):
        """Exception from pytesseract is caught — does not propagate to caller."""
        img = _make_img(1, 1)
        try:
            _main.extract_text_from_image(img)
        except Exception as e:
            self.fail(f"Exception propagated to caller: {e}")


# ---------------------------------------------------------------------------
# Tests — complexity regression (operation count, not wall-clock)
# ---------------------------------------------------------------------------
class TestExtractTextComplexityRegression(unittest.TestCase):
    """Representative regression: pytesseract called exactly once per call."""

    def setUp(self):
        _fake_pytesseract.image_to_string.reset_mock()
        _fake_pytesseract.image_to_string.return_value = "text"
        _fake_pytesseract.image_to_string.side_effect = None

    def test_one_ocr_call_per_invocation(self):
        """extract_text_from_image makes exactly 1 OCR call regardless of image size."""
        # Input sizes: n=1 (1×1), n=100 (10×10), n=10000 (100×100)
        for w, h in [(1, 1), (10, 10), (100, 100)]:
            _fake_pytesseract.image_to_string.reset_mock()
            img = _make_img(w, h)
            _main.extract_text_from_image(img)
            call_count = _fake_pytesseract.image_to_string.call_count
            self.assertEqual(
                call_count, 1,
                f"Expected 1 OCR call for {w}×{h} image, got {call_count}"
            )

    def test_five_repetitions_all_correct(self):
        """5 repetitions of ordinary input all return the same result."""
        # Fixed seed equivalent: same mock return value across repetitions
        # Expected: all 5 results == "text"
        img = _make_img(100, 100)
        results = [_main.extract_text_from_image(img) for _ in range(5)]
        self.assertEqual(len(set(results)), 1, "Results not consistent across 5 repetitions")
        self.assertEqual(results[0], "text")


if __name__ == "__main__":
    unittest.main(verbosity=2)
