import unittest
import sys
import os
from unittest.mock import patch, call

# Ensure target directory is in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import File_Renamer as fr


class TestFileRenamer(unittest.TestCase):
    """Focused refactoring and regression unit tests for File_Renamer."""

    def test_compute_renamed_filename_helper(self):
        """
        Verify the extracted compute_renamed_filename responsibility.
        """
        self.assertEqual(fr.compute_renamed_filename("photo.jpg", "vacation_", 0), "vacation_0.jpg")
        self.assertEqual(fr.compute_renamed_filename("data.tar.gz", "archive_", 3), "archive_3.gz")
        self.assertEqual(fr.compute_renamed_filename("file_no_ext", "out_", 1), "out_1.file_no_ext")

    def test_smallest_valid_input(self):
        """
        Smallest valid input: directory with 1 matching file.
        Precondition: Line 17 (os.listdir) and line 23 (re.match).
        """
        dir_path = "/fake/photos"
        fake_files = ["IMG_001.jpg"]

        with patch("os.listdir", return_value=fake_files), \
             patch("os.rename") as mock_rename:
            fr.rename_files(dir_path, r"IMG.*", "image_")
            mock_rename.assert_called_once_with(
                "/fake/photos/IMG_001.jpg",
                "/fake/photos/image_0.jpg"
            )

    def test_ordinary_valid_input(self):
        """
        Ordinary valid input: directory with multiple matching and non-matching files.
        """
        dir_path = "/fake/gallery"
        fake_files = ["IMG_10.png", "notes.txt", "IMG_20.png"]

        with patch("os.listdir", return_value=fake_files), \
             patch("os.rename") as mock_rename:
            fr.rename_files(dir_path, r"IMG.*", "pic_")
            expected_calls = [
                call("/fake/gallery/IMG_10.png", "/fake/gallery/pic_0.png"),
                call("/fake/gallery/IMG_20.png", "/fake/gallery/pic_1.png"),
            ]
            self.assertEqual(mock_rename.call_count, 2)
            mock_rename.assert_has_calls(expected_calls)

    def test_no_matches_no_renames(self):
        """
        Directory with no files matching pattern results in zero renames.
        """
        dir_path = "/fake/empty_matches"
        fake_files = ["a.txt", "b.txt"]

        with patch("os.listdir", return_value=fake_files), \
             patch("os.rename") as mock_rename:
            fr.rename_files(dir_path, r"IMG.*", "pic_")
            mock_rename.assert_not_called()


if __name__ == "__main__":
    unittest.main()
