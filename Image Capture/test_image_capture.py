import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Auto-add site-packages from .venv
for venv_path in [
    os.path.join(BASE_DIR, "..", "..", ".venv"),
    os.path.join(BASE_DIR, "..", ".venv"),
]:
    lib = os.path.join(venv_path, "lib")
    if os.path.exists(lib):
        for p in os.listdir(lib):
            sp = os.path.join(lib, p, "site-packages")
            if os.path.exists(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

import numpy as np
import take_pictures_from_webcam as cam_module


class MockVideoCapture:
    def __init__(self, total_frames=10, frame_shape=(480, 640, 3)):
        self.total_frames = total_frames
        self.frame_shape = frame_shape
        self.read_count = 0

    def read(self):
        if self.read_count < self.total_frames:
            self.read_count += 1
            frame = np.zeros(self.frame_shape, dtype=np.uint8)
            return True, frame
        return False, None


class TestImageCaptureWorkScaling(unittest.TestCase):
    """
    Focused tests measuring the work done by main / capture_session (take_pictures_from_webcam.py).
    Precondition source lines:
      - take_pictures_from_webcam.py:3 establishes cv2
      - take_pictures_from_webcam.py:14 establishes main / capture_session
      - take_pictures_from_webcam.py:20 establishes cv2.resize
      - take_pictures_from_webcam.py:27 establishes save trigger
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_process_frame_resizing_correctness(self):
        # Frame transform correctness
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        resized = cam_module.process_frame(frame, (600, 600))
        self.assertEqual(resized.shape, (600, 600, 3))

    def test_smallest_valid_input_1_frame(self):
        mock_cap = MockVideoCapture(total_frames=1)
        metrics = cam_module.capture_session(
            mock_cap,
            name="small",
            directory=self.temp_dir.name,
            max_frames=1,
            key_provider=lambda: ord("q"),
            show_ui=False,
            write_io=False,
        )
        self.assertEqual(metrics["frames_processed"], 1)
        self.assertEqual(metrics["resize_ops"], 1)
        self.assertGreaterEqual(metrics["algo_duration"], 0.0)

    def test_ordinary_valid_input_20_frames(self):
        mock_cap = MockVideoCapture(total_frames=20)
        # Save every 4th frame (5 frames saved total)
        key_seq = [ord(" ") if i % 4 == 0 else ord("x") for i in range(20)]
        key_iter = iter(key_seq)

        metrics = cam_module.capture_session(
            mock_cap,
            name="ordinary",
            directory=self.temp_dir.name,
            max_frames=20,
            key_provider=lambda: next(key_iter, -1),
            show_ui=False,
            write_io=True,
        )
        self.assertEqual(metrics["frames_processed"], 20)
        self.assertEqual(metrics["resize_ops"], 20)
        self.assertEqual(metrics["frames_saved"], 5)
        self.assertLess(metrics["algo_duration"], metrics["total_duration"])

    def test_work_scaling_linearity(self):
        # Measure scaling across varied input sizes N = [5, 10, 25, 50]
        test_sizes = [5, 10, 25, 50]
        scaling_results = []

        for n in test_sizes:
            cap = MockVideoCapture(total_frames=n)
            res = cam_module.capture_session(
                cap,
                name=f"scale_{n}",
                directory=self.temp_dir.name,
                max_frames=n,
                key_provider=lambda: ord("a"),
                show_ui=False,
                write_io=False,
            )
            self.assertEqual(res["frames_processed"], n)
            self.assertEqual(res["resize_ops"], n)
            scaling_results.append((n, res["resize_ops"], res["algo_duration"]))

        # Operation counts scale strictly linearly: O(N) where ops == N
        for n, ops, duration in scaling_results:
            self.assertEqual(ops, n)


if __name__ == "__main__":
    unittest.main()
