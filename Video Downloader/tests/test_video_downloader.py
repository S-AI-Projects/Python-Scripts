"""Focused tests for VideoDownloader.py; all external effects are mocked."""

import builtins
import importlib.util
import json
import os
import sys
import types
import unittest
from unittest.mock import Mock, patch


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_PATH = os.path.join(REPO_ROOT, "Video Downloader", "VideoDownloader.py")
FIXTURE_URL = "https://www.youtube.com/watch?v=fixture123"
FIXTURE_PATH = "/isolated/output/fixture123.mp4"
OTHER_URL = "https://www.youtube.com/watch?v=other456"
OTHER_PATH = "/isolated/output/other456.mp4"


def load_module():
    """Load a fresh instance of the named target module."""
    spec = importlib.util.spec_from_file_location("VideoDownloader", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load target module at {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_mocked_download(module, url, expected_path):
    """Call the target with network and filesystem effects replaced by mocks."""
    fake_stream = Mock()
    fake_stream.download.return_value = expected_path
    fake_streams = Mock()
    fake_streams.get_highest_resolution.return_value = fake_stream
    fake_video = Mock()
    fake_video.streams = fake_streams
    youtube_factory = Mock(return_value=fake_video)
    pytube_module = types.ModuleType("pytube")
    pytube_module.YouTube = youtube_factory

    with patch.dict(sys.modules, {"pytube": pytube_module}):
        result = module.download_video(url)

    youtube_factory.assert_called_once_with(url)
    fake_streams.get_highest_resolution.assert_called_once_with()
    fake_stream.download.assert_called_once_with()
    return result


class VideoDownloaderTests(unittest.TestCase):
    def test_import_has_no_prompt_or_external_dependency_access(self):
        with patch.object(builtins, "input") as mocked_input, patch.object(
            builtins, "__import__", wraps=builtins.__import__
        ) as mocked_import:
            module = load_module()
        mocked_input.assert_not_called()
        imported_modules = [call.args[0] for call in mocked_import.call_args_list]
        self.assertNotIn("pytube", imported_modules)
        self.assertTrue(callable(module.download_video))
        self.assertTrue(callable(module.main))

    def test_download_uses_highest_resolution_and_returns_saved_path(self):
        module = load_module()
        actual = run_mocked_download(module, FIXTURE_URL, FIXTURE_PATH)
        self.assertEqual(FIXTURE_PATH, actual)

    def test_repeated_and_interleaved_inputs_are_order_independent(self):
        # Two identical runs start with a fresh module and fresh mocked dependency state.
        first = run_mocked_download(load_module(), FIXTURE_URL, FIXTURE_PATH)
        second = run_mocked_download(load_module(), FIXTURE_URL, FIXTURE_PATH)

        # Reuse one module for a fixture, another valid URL, and the fixture again.
        sequence_module = load_module()
        before_other = run_mocked_download(sequence_module, FIXTURE_URL, FIXTURE_PATH)
        other = run_mocked_download(sequence_module, OTHER_URL, OTHER_PATH)
        after_other = run_mocked_download(sequence_module, FIXTURE_URL, FIXTURE_PATH)

        self.assertEqual(FIXTURE_PATH, first)
        self.assertEqual(FIXTURE_PATH, second)
        self.assertEqual(FIXTURE_PATH, before_other)
        self.assertEqual(OTHER_PATH, other)
        self.assertEqual(FIXTURE_PATH, after_other)
        self.assertEqual(first, second)
        self.assertEqual(before_other, after_other)

        observations_path = os.environ.get("R35_T055_OBSERVATIONS_PATH")
        if observations_path:
            observations = {
                "same_fixture_fresh_isolated_runs": [first, second],
                "after_another_valid_input": {
                    "before_other_input": before_other,
                    "other_valid_input_result": other,
                    "fixture_after_other_input": after_other,
                },
            }
            with open(observations_path, "w", encoding="utf-8") as file:
                json.dump(observations, file, indent=2)

    def test_main_reads_one_url_and_downloads_it(self):
        module = load_module()
        fake_stream = Mock()
        fake_stream.download.return_value = FIXTURE_PATH
        fake_video = Mock()
        fake_video.streams.get_highest_resolution.return_value = fake_stream
        youtube_factory = Mock(return_value=fake_video)
        pytube_module = types.ModuleType("pytube")
        pytube_module.YouTube = youtube_factory

        with patch.object(builtins, "input", return_value=FIXTURE_URL) as mocked_input, patch.dict(
            sys.modules, {"pytube": pytube_module}
        ):
            result = module.main()

        mocked_input.assert_called_once_with("Enter the link: ")
        youtube_factory.assert_called_once_with(FIXTURE_URL)
        fake_video.streams.get_highest_resolution.assert_called_once_with()
        fake_stream.download.assert_called_once_with()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
