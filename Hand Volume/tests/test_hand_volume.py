import io
import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

# Ensure 'Hand Volume' directory is in sys.path
HAND_VOLUME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if HAND_VOLUME_DIR not in sys.path:
    sys.path.insert(0, HAND_VOLUME_DIR)

import main


class TestHandVolume(unittest.TestCase):
    """Partition testing and boundary regression tests for Hand Volume module."""

    # =========================================================================
    # Partition 1: Distance to Percent (distance_to_percent)
    # Valid Boundary: 50.0 (lower), 250.0 (upper)
    # Valid Interior: 50.0 < distance < 250.0
    # =========================================================================

    def test_distance_to_percent_lower_boundary(self):
        """Test exact lower boundary at distance = 50.0 -> Percent = 0."""
        self.assertEqual(main.distance_to_percent(50.0), 0)

    def test_distance_to_percent_below_lower_boundary(self):
        """Test values below lower boundary (< 50.0) clamp to 0."""
        # Just below boundary
        self.assertEqual(main.distance_to_percent(49.0), 0)
        # Deeply below boundary
        self.assertEqual(main.distance_to_percent(0.0), 0)
        # Negative value (source leaves behavior undefined, clamps without artificial rejection)
        self.assertEqual(main.distance_to_percent(-20.0), 0)

    def test_distance_to_percent_above_lower_boundary(self):
        """Test value just above lower boundary (> 50.0, interior) -> Percent = 1."""
        self.assertEqual(main.distance_to_percent(52.0), 1)

    def test_distance_to_percent_valid_interior(self):
        """Test representative interior values between 50.0 and 250.0."""
        self.assertEqual(main.distance_to_percent(150.0), 50)
        self.assertEqual(main.distance_to_percent(70.0), 10)
        self.assertEqual(main.distance_to_percent(210.0), 80)

    def test_distance_to_percent_upper_boundary(self):
        """Test exact upper boundary at distance = 250.0 -> Percent = 100."""
        self.assertEqual(main.distance_to_percent(250.0), 100)

    def test_distance_to_percent_below_upper_boundary(self):
        """Test value just below upper boundary (< 250.0, interior) -> Percent = 99."""
        self.assertEqual(main.distance_to_percent(248.0), 99)

    def test_distance_to_percent_above_upper_boundary(self):
        """Test values above upper boundary (> 250.0) clamp to 100."""
        # Just above boundary
        self.assertEqual(main.distance_to_percent(252.0), 100)
        # Deeply above boundary
        self.assertEqual(main.distance_to_percent(350.0), 100)

    def test_distance_to_percent_unsupported_type(self):
        """Test explicitly unsupported non-numeric types raise TypeError."""
        with self.assertRaises(TypeError):
            main.distance_to_percent(None)
        with self.assertRaises(TypeError):
            main.distance_to_percent("invalid")

    # =========================================================================
    # Partition 2: Volume Change Calculation (percent_to_volume_change)
    # Formula: round(math.log((Percent / 10) + 1) * 50 * 0.54)
    # Boundary: Percent = 0 (0 dB change)
    # Domain boundary: (Percent / 10) + 1 > 0 -> Percent > -10
    # Boundary: Percent = 100 (65 dB change)
    # =========================================================================

    def test_percent_to_volume_change_lower_boundary(self):
        """Test exact lower boundary Percent = 0 -> Changevolume = 0."""
        self.assertEqual(main.percent_to_volume_change(0), 0)

    def test_percent_to_volume_change_above_lower_boundary(self):
        """Test value above lower boundary (interior) -> Percent = 10 -> Changevolume = 19."""
        self.assertEqual(main.percent_to_volume_change(10), 19)

    def test_percent_to_volume_change_domain_boundary_unsupported(self):
        """Test explicitly unsupported domain values Percent <= -10 raise ValueError (math domain error)."""
        # Exactly at domain boundary where argument is 0 (log(0) undefined)
        with self.assertRaises(ValueError):
            main.percent_to_volume_change(-10)
        # Strictly below domain boundary where argument is negative
        with self.assertRaises(ValueError):
            main.percent_to_volume_change(-15)

    def test_percent_to_volume_change_valid_interior(self):
        """Test interior values between 0 and 100."""
        # 50% volume
        self.assertEqual(main.percent_to_volume_change(50), 48)
        # 25% volume
        self.assertEqual(main.percent_to_volume_change(25), 34)

    def test_percent_to_volume_change_upper_boundary(self):
        """Test exact upper boundary Percent = 100 -> Changevolume = 65."""
        self.assertEqual(main.percent_to_volume_change(100), 65)

    def test_percent_to_volume_change_below_upper_boundary(self):
        """Test value just below upper boundary Percent = 90 -> Changevolume = 62."""
        self.assertEqual(main.percent_to_volume_change(90), 62)

    def test_percent_to_volume_change_above_upper_boundary(self):
        """Test value above 100% (unclamped by formula) Percent = 110 -> Changevolume = 67."""
        self.assertEqual(main.percent_to_volume_change(110), 67)

    def test_percent_to_volume_change_unsupported_type(self):
        """Test explicitly unsupported non-numeric types raise TypeError."""
        with self.assertRaises(TypeError):
            main.percent_to_volume_change("bad")
        with self.assertRaises(TypeError):
            main.percent_to_volume_change(None)

    # =========================================================================
    # Partition 3: Volume Bar Height (percent_to_bar_height)
    # Formula: int(340 - (Percent * 2.0))
    # Boundary: Percent = 0 -> 340 (empty bar)
    # Boundary: Percent = 100 -> 140 (full bar)
    # =========================================================================

    def test_percent_to_bar_height_lower_boundary(self):
        """Test boundary Percent = 0 -> height = 340."""
        self.assertEqual(main.percent_to_bar_height(0), 340)

    def test_percent_to_bar_height_below_lower_boundary(self):
        """Test side below lower boundary Percent = -5 -> height = 350."""
        self.assertEqual(main.percent_to_bar_height(-5), 350)

    def test_percent_to_bar_height_above_lower_boundary(self):
        """Test side above lower boundary Percent = 5 -> height = 330."""
        self.assertEqual(main.percent_to_bar_height(5), 330)

    def test_percent_to_bar_height_interior(self):
        """Test interior Percent = 50 -> height = 240."""
        self.assertEqual(main.percent_to_bar_height(50), 240)

    def test_percent_to_bar_height_upper_boundary(self):
        """Test boundary Percent = 100 -> height = 140."""
        self.assertEqual(main.percent_to_bar_height(100), 140)

    def test_percent_to_bar_height_below_upper_boundary(self):
        """Test side below upper boundary Percent = 95 -> height = 150."""
        self.assertEqual(main.percent_to_bar_height(95), 150)

    def test_percent_to_bar_height_above_upper_boundary(self):
        """Test side above upper boundary Percent = 105 -> height = 130."""
        self.assertEqual(main.percent_to_bar_height(105), 130)

    # =========================================================================
    # Partition 4: Euclidean Distance (calculate_distance)
    # Boundary: coincident points (distance = 0.0)
    # Interior: distance > 0.0
    # =========================================================================

    def test_calculate_distance_coincident_boundary(self):
        """Test boundary at identical points -> distance = 0.0."""
        self.assertEqual(main.calculate_distance((100, 100), (100, 100)), 0.0)
        self.assertEqual(main.calculate_distance(50, 50, 50, 50), 0.0)

    def test_calculate_distance_strictly_positive(self):
        """Test side above 0 boundary (strictly positive distance)."""
        self.assertEqual(main.calculate_distance((0, 0), (3, 4)), 5.0)

    def test_calculate_distance_interior(self):
        """Test realistic landmark distance."""
        self.assertEqual(main.calculate_distance((100, 100), (220, 260)), 200.0)

    # =========================================================================
    # Partition 5: Finger Detection & Safe Execution
    # =========================================================================

    def test_detect_fingers_empty_boundary(self):
        """Test empty landmark list boundary -> returns []."""
        self.assertEqual(main.detect_fingers([]), [])

    def test_detect_fingers_gesture_interior(self):
        """Test finger detection with 21 mock landmarks (Thumb & Index extended)."""
        mock_lms = [[i, 100, 100] for i in range(21)]
        # Thumb tip (4) x > ip (3) x -> Thumb UP
        mock_lms[4][1] = 150
        mock_lms[3][1] = 120
        # Index tip (8) y < pip (6) y -> Index UP
        mock_lms[8][2] = 50
        mock_lms[6][2] = 90
        # Middle tip (12) y > pip (10) y -> Middle DOWN
        mock_lms[12][2] = 120
        mock_lms[10][2] = 90
        # Ring tip (16) y > pip (14) y -> Ring DOWN
        mock_lms[16][2] = 120
        mock_lms[14][2] = 90
        # Pinky tip (20) y > pip (18) y -> Pinky DOWN
        mock_lms[20][2] = 120
        mock_lms[18][2] = 90

        result = main.detect_fingers(mock_lms)
        self.assertEqual(result, [1, 1, 0, 0, 0])

    def test_safe_import_and_mocked_loop(self):
        """Test running main loop with mocked I/O and bounded iterations."""
        mock_cap = MagicMock()
        mock_cap.read.return_value = (True, MagicMock())
        mock_vol = MagicMock()
        mock_detector = MagicMock()
        mock_detector.findHands.return_value = MagicMock()
        mock_detector.findPosition.return_value = []

        with patch("sys.stdout", new_callable=io.StringIO):
            main.main(cap=mock_cap, vol=mock_vol, detector=mock_detector, max_iterations=1)
        mock_cap.read.assert_called_once()
        mock_vol.SetMasterVolumeLevel.assert_called_once()


if __name__ == "__main__":
    unittest.main()
