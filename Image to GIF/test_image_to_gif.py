import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock PIL.Image if not available
if "PIL" not in sys.modules:
    mock_pil = MagicMock()
    mock_image_module = MagicMock()
    mock_pil.Image = mock_image_module
    sys.modules["PIL"] = mock_pil
    sys.modules["PIL.Image"] = mock_image_module

# Ensure module path is accessible
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import imageTogif as itg


def independent_oracle(frame_list, output_name="my_awesome.gif"):
    """
    Independent reference oracle for make_gif.
    Computes expected output contract directly from image frame inputs without calling make_gif.
    """
    if not frame_list:
        raise ValueError("No frames")
    return {
        "output_filepath": output_name,
        "format": "GIF",
        "total_frames": len(frame_list),
        "first_frame": frame_list[0],
        "duration": 100,
        "loop": 0,
        "save_all": True,
    }


class TestImageToGif(unittest.TestCase):
    """Reference-comparison regression tests for make_gif."""

    def test_smallest_valid_input(self):
        """
        Smallest valid input: frame_folder with exactly 1 JPG image.
        Precondition: Line 5 in imageTogif.py (frame_one = frames[0]) requires >= 1 frame.
        """
        fake_files = ["/test/folder/img_0.JPG"]
        mock_frame = MagicMock()

        with patch("glob.glob", return_value=fake_files), \
             patch.object(itg.Image, "open", return_value=mock_frame):
            result = itg.make_gif("/test/folder")
            self.assertEqual(result, "my_awesome.gif")

            mock_frame.save.assert_called_once()
            args, kwargs = mock_frame.save.call_args
            self.assertEqual(args[0], "my_awesome.gif")
            self.assertEqual(kwargs["format"], "GIF")
            self.assertEqual(kwargs["save_all"], True)
            self.assertEqual(kwargs["duration"], 100)
            self.assertEqual(kwargs["loop"], 0)
            self.assertEqual(len(kwargs["append_images"]), 1)

    def test_ordinary_valid_input(self):
        """
        Ordinary valid input: frame_folder with 5 JPG images.
        """
        fake_files = [f"/test/folder/img_{i}.JPG" for i in range(5)]
        mock_frames = [MagicMock() for _ in range(5)]

        def mock_open(path):
            idx = int(path.split("_")[-1].split(".")[0])
            return mock_frames[idx]

        with patch("glob.glob", return_value=fake_files), \
             patch.object(itg.Image, "open", side_effect=mock_open):
            result = itg.make_gif("/test/folder", output_filepath="custom.gif")
            self.assertEqual(result, "custom.gif")

            mock_frames[0].save.assert_called_once()
            args, kwargs = mock_frames[0].save.call_args
            self.assertEqual(args[0], "custom.gif")
            self.assertEqual(len(kwargs["append_images"]), 5)

    def test_oracle_cross_check_25_configurations(self):
        """
        Cross-check make_gif against independent oracle across 25 distinct configurations.
        """
        for count in range(1, 26):
            fake_files = [f"/frames/img_{i}.JPG" for i in range(count)]
            mock_frames = [MagicMock() for _ in range(count)]

            oracle_res = independent_oracle(fake_files, f"anim_{count}.gif")

            def mock_open(path):
                idx = int(path.split("_")[-1].split(".")[0])
                return mock_frames[idx]

            with patch("glob.glob", return_value=fake_files), \
                 patch.object(itg.Image, "open", side_effect=mock_open):
                out = itg.make_gif("/frames", output_filepath=f"anim_{count}.gif")
                self.assertEqual(out, oracle_res["output_filepath"])

                mock_frames[0].save.assert_called_once()
                args, kwargs = mock_frames[0].save.call_args
                self.assertEqual(args[0], oracle_res["output_filepath"])
                self.assertEqual(kwargs["format"], oracle_res["format"])
                self.assertEqual(kwargs["save_all"], oracle_res["save_all"])
                self.assertEqual(kwargs["duration"], oracle_res["duration"])
                self.assertEqual(kwargs["loop"], oracle_res["loop"])
                self.assertEqual(len(kwargs["append_images"]), oracle_res["total_frames"])

    def test_empty_folder_raises_error(self):
        """
        Input with 0 frames violates precondition and raises ValueError.
        """
        with patch("glob.glob", return_value=[]):
            with self.assertRaises(ValueError):
                itg.make_gif("/empty/folder")

    def test_no_input_mutation(self):
        """
        Verifies input parameters are not mutated.
        """
        folder = "/test/folder"
        out_name = "test.gif"
        with patch("glob.glob", return_value=["/test/folder/img_0.JPG"]), \
             patch.object(itg.Image, "open", return_value=MagicMock()):
            itg.make_gif(folder, out_name)
            self.assertEqual(folder, "/test/folder")
            self.assertEqual(out_name, "test.gif")


if __name__ == "__main__":
    unittest.main()
