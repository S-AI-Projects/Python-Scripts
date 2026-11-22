import importlib
import io
import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

# Ensure 'Font Art' directory is in sys.path
FONT_ART_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if FONT_ART_DIR not in sys.path:
    sys.path.insert(0, FONT_ART_DIR)


class TestFontArt(unittest.TestCase):
    """Regression and unit tests for Font Art module."""

    def setUp(self):
        self.mock_figlet_cls = MagicMock()
        self.mock_figlet_instance = MagicMock()
        self.mock_figlet_cls.return_value = self.mock_figlet_instance

        self.expected_default_art = (
            "    ____  __                                __       _   __\n"
            "   / __ \\/ /_  ____ _____  __  ___________ / /_     / | / /\n"
            "  / / / / __ \\/ __ `/ __ \\/ / / / ___/ __ \\/ __ \\   /  |/ / \n"
            " / /_/ / / / / /_/ / / / / /_/ (__  ) / / / / / /  / /|  /  \n"
            "/_____/_/ /_/\\__,_/_/ /_/\\__,_/____/_/ /_/_/ /_/  /_/ |_/   \n"
        )
        self.mock_figlet_instance.renderText.return_value = self.expected_default_art

    def test_render_font_art_default_content(self):
        """Assert render_font_art uses default text 'Dhanush N' and font 'slant'."""
        with patch.dict(sys.modules, {"pyfiglet": MagicMock(Figlet=self.mock_figlet_cls)}):
            import FontArt
            with patch.object(FontArt, "Figlet", self.mock_figlet_cls):
                result = FontArt.render_font_art()

                self.mock_figlet_cls.assert_called_with(font="slant")
                self.mock_figlet_instance.renderText.assert_called_with("Dhanush N")
                self.assertEqual(result, self.expected_default_art)

    def test_render_font_art_custom_content(self):
        """Assert render_font_art accepts custom text and font and renders them."""
        custom_art = "CUSTOM_ASCII_ART"
        self.mock_figlet_instance.renderText.return_value = custom_art

        with patch.dict(sys.modules, {"pyfiglet": MagicMock(Figlet=self.mock_figlet_cls)}):
            import FontArt
            with patch.object(FontArt, "Figlet", self.mock_figlet_cls):
                result = FontArt.render_font_art(text="Custom Message", font="banner")

                self.mock_figlet_cls.assert_called_with(font="banner")
                self.mock_figlet_instance.renderText.assert_called_with("Custom Message")
                self.assertEqual(result, custom_art)

    def test_render_font_art_missing_dependency(self):
        """Assert ImportError is raised with informative message when pyfiglet is unavailable."""
        import FontArt
        with patch.object(FontArt, "Figlet", None):
            with patch.dict(sys.modules, {"pyfiglet": None}):
                with self.assertRaises(ImportError) as ctx:
                    FontArt.render_font_art()
                self.assertIn("pyfiglet is required", str(ctx.exception))

    def test_display_font_art_windows(self):
        """Assert display_font_art executes 'cls' and 'mode con:' on Windows and prints art."""
        with patch.dict(sys.modules, {"pyfiglet": MagicMock(Figlet=self.mock_figlet_cls)}):
            import FontArt
            with patch.object(FontArt, "Figlet", self.mock_figlet_cls), \
                 patch("os.name", "nt"), \
                 patch("os.system") as mock_system, \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:

                result = FontArt.display_font_art()

                expected_calls = [
                    call("cls"),
                    call("mode con: cols=75 lines=30"),
                ]
                mock_system.assert_has_calls(expected_calls, any_order=False)
                self.assertEqual(mock_system.call_count, 2)
                self.assertEqual(mock_stdout.getvalue(), f"{self.expected_default_art}\n")
                self.assertEqual(result, self.expected_default_art)

    def test_display_font_art_posix(self):
        """Assert display_font_art executes 'clear' on POSIX without Windows mode con."""
        with patch.dict(sys.modules, {"pyfiglet": MagicMock(Figlet=self.mock_figlet_cls)}):
            import FontArt
            with patch.object(FontArt, "Figlet", self.mock_figlet_cls), \
                 patch("os.name", "posix"), \
                 patch("os.system") as mock_system, \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:

                result = FontArt.display_font_art()

                mock_system.assert_called_once_with("clear")
                called_commands = [c[0][0] for c in mock_system.call_args_list]
                self.assertNotIn("cls", called_commands)
                self.assertTrue(all("mode con:" not in cmd for cmd in called_commands))
                self.assertEqual(mock_stdout.getvalue(), f"{self.expected_default_art}\n")
                self.assertEqual(result, self.expected_default_art)

    def test_safe_import_no_side_effects(self):
        """Assert importing FontArt does not execute terminal commands or print to stdout."""
        with patch.dict(sys.modules, {"pyfiglet": MagicMock(Figlet=self.mock_figlet_cls)}):
            with patch("os.system") as mock_system, \
                 patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:

                if "FontArt" in sys.modules:
                    importlib.reload(sys.modules["FontArt"])
                else:
                    importlib.import_module("FontArt")

                self.assertEqual(mock_system.call_count, 0)
                self.assertEqual(mock_stdout.getvalue(), "")

    def test_main_entrypoint(self):
        """Assert main() invokes display_font_art with default configuration."""
        with patch.dict(sys.modules, {"pyfiglet": MagicMock(Figlet=self.mock_figlet_cls)}):
            import FontArt
            with patch.object(FontArt, "display_font_art") as mock_display:
                FontArt.main()
                mock_display.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
