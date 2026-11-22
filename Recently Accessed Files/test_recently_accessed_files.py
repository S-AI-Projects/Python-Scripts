"""Tests for Recently Accessed Files/recently_accessed_files.py — R35-T010.

Fixture (written BEFORE editing the implementation):
    Smallest valid input : file_path="" → os.path.getatime("") mocked to 1000.0
    Ordinary input       : file_path="/home/user/document.txt" → getatime mocked to 5000.0

Precondition anchor:
    ``def get_file_access_time(file_path):``  # line 4
    ``recently_accessed_files = []``          # line 9 (data anchor)

Mutation-resistant test target:
    Plausible one-line mistake: ``os.path.getmtime`` instead of ``os.path.getatime``.
    Mocking both with different values (getatime=1000.0, getmtime=2000.0) lets the
    test distinguish the original from the mutant by asserting the return equals
    the getatime value.
"""

import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, "Recently Accessed Files")
import recently_accessed_files as raf  # noqa: E402


# ---------------------------------------------------------------------------
# Tests — smallest valid input
# ---------------------------------------------------------------------------
class TestGetFileAccessTimeSmallestInput(unittest.TestCase):
    """get_file_access_time with the smallest valid input: file_path=""."""

    def test_smallest_returns_getatime_value(self):
        """Smallest input ("") → returns os.path.getatime("") value (1000.0)."""
        # Precondition anchor: def get_file_access_time(file_path):  # line 4
        # Expected: 1000.0  (independently established before editing)
        with patch("recently_accessed_files.os.path.getatime", return_value=1000.0):
            result = raf.get_file_access_time("")
        self.assertEqual(result, 1000.0)

    def test_smallest_returns_float(self):
        """Smallest input → result is a float (Unix timestamp)."""
        # Expected: float
        with patch("recently_accessed_files.os.path.getatime", return_value=1000.0):
            result = raf.get_file_access_time("")
        self.assertIsInstance(result, float)

    def test_smallest_no_mutation(self):
        """Input string is not mutated by get_file_access_time."""
        path = ""
        with patch("recently_accessed_files.os.path.getatime", return_value=1000.0):
            raf.get_file_access_time(path)
        self.assertEqual(path, "")  # unchanged


# ---------------------------------------------------------------------------
# Tests — ordinary input
# ---------------------------------------------------------------------------
class TestGetFileAccessTimeOrdinaryInput(unittest.TestCase):
    """get_file_access_time with ordinary input: "/home/user/document.txt"."""

    _PATH = "/home/user/document.txt"

    def test_ordinary_returns_getatime_value(self):
        """Ordinary input → returns os.path.getatime value (5000.0)."""
        # Precondition anchor: def get_file_access_time(file_path):  # line 4
        # Expected: 5000.0  (independently established before editing)
        with patch("recently_accessed_files.os.path.getatime", return_value=5000.0):
            result = raf.get_file_access_time(self._PATH)
        self.assertEqual(result, 5000.0)

    def test_ordinary_passes_path_to_getatime(self):
        """get_file_access_time passes file_path exactly to os.path.getatime."""
        # Expected: getatime called with "/home/user/document.txt"
        with patch("recently_accessed_files.os.path.getatime", return_value=5000.0) as mock_atime:
            raf.get_file_access_time(self._PATH)
        mock_atime.assert_called_once_with(self._PATH)


# ---------------------------------------------------------------------------
# Mutation-resistant tests
# ---------------------------------------------------------------------------
class TestGetFileAccessTimeMutationResistant(unittest.TestCase):
    """Regression tests that detect the getmtime-for-getatime one-line mutant.

    Plausible mutation: ``return os.path.getmtime(file_path)``
    Strategy: mock getatime=1000.0 and getmtime=2000.0; assert result==1000.0.
    Original returns 1000.0 (PASS); mutant returns 2000.0 (FAIL).
    """

    def test_returns_atime_not_mtime(self):
        """get_file_access_time returns getatime value, NOT getmtime value.

        Protected condition: ``os.path.getatime`` (access time), not ``getmtime``.
        Mutant (getmtime) returns 2000.0; original returns 1000.0.
        """
        # Precondition anchor: def get_file_access_time(file_path):  # line 4
        # Independently established: getatime("") == 1000.0 (not 2000.0)
        with patch("recently_accessed_files.os.path.getatime", return_value=1000.0), \
             patch("recently_accessed_files.os.path.getmtime", return_value=2000.0):
            result = raf.get_file_access_time("")
        self.assertEqual(result, 1000.0,
            "Expected getatime value 1000.0; getmtime mutant would return 2000.0")

    def test_returns_atime_not_ctime(self):
        """get_file_access_time returns getatime value, NOT getctime value.

        Protected condition: ``os.path.getatime`` (access time), not ``getctime``.
        Mutant (getctime) returns 3000.0; original returns 1000.0.
        """
        # Independently established: getatime("") == 1000.0 (not 3000.0)
        with patch("recently_accessed_files.os.path.getatime", return_value=1000.0), \
             patch("recently_accessed_files.os.path.getctime", return_value=3000.0):
            result = raf.get_file_access_time("")
        self.assertEqual(result, 1000.0,
            "Expected getatime value 1000.0; getctime mutant would return 3000.0")

    def test_distinct_atime_mtime_ordinary(self):
        """Ordinary input: different atime and mtime — returns atime."""
        # file_path="/home/user/document.txt", getatime=5000.0, getmtime=9999.0
        with patch("recently_accessed_files.os.path.getatime", return_value=5000.0), \
             patch("recently_accessed_files.os.path.getmtime", return_value=9999.0):
            result = raf.get_file_access_time("/home/user/document.txt")
        self.assertEqual(result, 5000.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
