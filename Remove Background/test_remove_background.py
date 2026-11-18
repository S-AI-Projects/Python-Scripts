import os
import sys
import unittest
import numpy as np

# Ensure Remove Background directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import code as rb_module


class TestRemoveBackgroundBoundaries(unittest.TestCase):
    """
    Focused boundary unit tests for Remove Background (code.py).
    Precondition source lines:
      - code.py:1 establishes module imports and definitions.
      - code.py:5 establishes remove_background contract and preconditions.
    """

    def test_smallest_valid_input_1x1(self):
        # Smallest valid input: 1x1 3-channel BGR image
        tiny_bgr = np.zeros((1, 1, 3), dtype=np.uint8)
        tiny_bgr[0, 0] = [120, 130, 140]

        res = rb_module.remove_background(tiny_bgr, threshold=250)
        self.assertEqual(res.shape, (1, 1, 4))
        self.assertEqual(res.dtype, np.uint8)
        # BGR channels are preserved
        np.testing.assert_array_equal(res[0, 0, :3], tiny_bgr[0, 0, :3])

    def test_ordinary_valid_input_100x100(self):
        # Ordinary input: 100x100 3-channel BGR image
        ord_bgr = np.full((100, 100, 3), 200, dtype=np.uint8)
        res = rb_module.remove_background(ord_bgr, threshold=250)
        self.assertEqual(res.shape, (100, 100, 4))
        self.assertEqual(res.dtype, np.uint8)
        np.testing.assert_array_equal(res[:, :, :3], ord_bgr)

    def test_threshold_lower_boundary_0(self):
        # Boundary: threshold = 0
        img = np.full((10, 10, 3), 100, dtype=np.uint8)
        res = rb_module.remove_background(img, threshold=0)
        self.assertEqual(res.shape, (10, 10, 4))

    def test_threshold_upper_boundary_255(self):
        # Boundary: threshold = 255
        img = np.full((10, 10, 3), 100, dtype=np.uint8)
        res = rb_module.remove_background(img, threshold=255)
        self.assertEqual(res.shape, (10, 10, 4))

    def test_unsupported_none_input(self):
        # Unsupported: None
        with self.assertRaises(ValueError):
            rb_module.remove_background(None)

    def test_unsupported_non_3channel_shape(self):
        # Unsupported: 2D grayscale array
        gray_2d = np.zeros((20, 20), dtype=np.uint8)
        with self.assertRaises(ValueError):
            rb_module.remove_background(gray_2d)

    def test_unsupported_zero_dimension(self):
        # Unsupported: 0x0x3 array
        empty_img = np.zeros((0, 0, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            rb_module.remove_background(empty_img)

    def test_unsupported_threshold_out_of_bounds(self):
        img = np.zeros((5, 5, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            rb_module.remove_background(img, threshold=-1)
        with self.assertRaises(ValueError):
            rb_module.remove_background(img, threshold=256)


if __name__ == '__main__':
    unittest.main()
