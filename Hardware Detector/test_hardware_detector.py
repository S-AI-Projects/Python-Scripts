import unittest
from unittest.mock import patch, MagicMock
from collections import namedtuple
import sys
import os
import glob as glob_module

# Ensure psutil is available
try:
    import psutil
except ImportError:
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import psutil

sys.path.insert(0, os.path.dirname(__file__))
import hardware_detector as hd

VMem = namedtuple("VMem", ["total", "used"])
DiskUsage = namedtuple("DiskUsage", ["free"])


def independent_oracle_calculator(total_bytes, used_bytes, free_disk_bytes, cores, usage_pct):
    """
    Independent reference oracle using a separate calculation approach (direct float division + rounding).
    """
    GIB = 1073741824.0
    return {
        'ram_total_gb': round(total_bytes / GIB, 2),
        'ram_used_gb': round(used_bytes / GIB, 2),
        'available_diskspace_gb': round(free_disk_bytes / GIB, 2),
        'cpu_cores': int(cores),
        'cpu_usage_percent': float(usage_pct),
    }


class TestHardwareDetectorComparison(unittest.TestCase):
    def test_anchor_initialization(self):
        # Line 34: self.hardware_profile = {}
        detector = hd.HardwareDetector()
        self.assertEqual(detector.hardware_profile, {})

    @patch("psutil.cpu_percent")
    @patch("psutil.cpu_count")
    @patch("psutil.disk_usage")
    @patch("psutil.virtual_memory")
    def test_smallest_valid_input(self, mock_vmem, mock_disk, mock_cpu_count, mock_cpu_percent):
        # Smallest valid input: 1 GB total RAM (1073741824 bytes), 0 used, 1 GB free disk, 1 core, 0.0% CPU
        total_ram = 1073741824
        used_ram = 0
        free_disk = 1073741824
        cores = 1
        cpu_pct = 0.0

        mock_vmem.return_value = VMem(total=total_ram, used=used_ram)
        mock_disk.return_value = DiskUsage(free=free_disk)
        mock_cpu_count.return_value = cores
        mock_cpu_percent.return_value = cpu_pct

        detector = hd.HardwareDetector()
        detector.get_computer_specs()

        expected = independent_oracle_calculator(total_ram, used_ram, free_disk, cores, cpu_pct)
        self.assertEqual(detector.hardware_profile, expected)
        self.assertEqual(detector.hardware_profile['ram_total_gb'], 1.0)
        self.assertEqual(detector.hardware_profile['ram_used_gb'], 0.0)
        self.assertEqual(detector.hardware_profile['available_diskspace_gb'], 1.0)
        self.assertEqual(detector.hardware_profile['cpu_cores'], 1)
        self.assertEqual(detector.hardware_profile['cpu_usage_percent'], 0.0)

    @patch("psutil.cpu_percent")
    @patch("psutil.cpu_count")
    @patch("psutil.disk_usage")
    @patch("psutil.virtual_memory")
    def test_ordinary_valid_input(self, mock_vmem, mock_disk, mock_cpu_count, mock_cpu_percent):
        # Ordinary input: 16 GB total RAM, 8 GB used, 100 GB disk free, 8 cores, 15.5% CPU
        total_ram = 16 * 1073741824
        used_ram = 8 * 1073741824
        free_disk = 100 * 1073741824
        cores = 8
        cpu_pct = 15.5

        mock_vmem.return_value = VMem(total=total_ram, used=used_ram)
        mock_disk.return_value = DiskUsage(free=free_disk)
        mock_cpu_count.return_value = cores
        mock_cpu_percent.return_value = cpu_pct

        detector = hd.HardwareDetector()
        detector.get_computer_specs()

        expected = independent_oracle_calculator(total_ram, used_ram, free_disk, cores, cpu_pct)
        self.assertEqual(detector.hardware_profile, expected)

    @patch("psutil.cpu_percent")
    @patch("psutil.cpu_count")
    @patch("psutil.disk_usage")
    @patch("psutil.virtual_memory")
    def test_cross_check_25_synthetic_profiles(self, mock_vmem, mock_disk, mock_cpu_count, mock_cpu_percent):
        # Enumerate 25 distinct valid system profiles and cross-check against independent oracle
        test_cases = [
            (2 * (1024**3), 1 * (1024**3), 50 * (1024**3), 2, 5.0),
            (4 * (1024**3), 2 * (1024**3), 120 * (1024**3), 4, 10.2),
            (8 * (1024**3), 4 * (1024**3), 250 * (1024**3), 4, 25.4),
            (16 * (1024**3), 12 * (1024**3), 500 * (1024**3), 8, 45.0),
            (32 * (1024**3), 16 * (1024**3), 1000 * (1024**3), 16, 75.8),
            (64 * (1024**3), 32 * (1024**3), 2000 * (1024**3), 32, 90.1),
            (128 * (1024**3), 64 * (1024**3), 4000 * (1024**3), 64, 99.9),
            (3 * (1024**3), 1 * (1024**3), 10 * (1024**3), 2, 1.1),
            (6 * (1024**3), 3 * (1024**3), 80 * (1024**3), 6, 12.3),
            (12 * (1024**3), 6 * (1024**3), 150 * (1024**3), 6, 33.7),
            (24 * (1024**3), 10 * (1024**3), 300 * (1024**3), 12, 50.0),
            (48 * (1024**3), 20 * (1024**3), 750 * (1024**3), 24, 66.2),
            (1 * (1024**3), 512 * (1024**2), 5 * (1024**3), 1, 0.5),
            (8 * (1024**3), 7 * (1024**3), 30 * (1024**3), 4, 88.4),
            (16 * (1024**3), 2 * (1024**3), 450 * (1024**3), 8, 8.9),
            (32 * (1024**3), 28 * (1024**3), 900 * (1024**3), 16, 92.5),
            (64 * (1024**3), 8 * (1024**3), 1800 * (1024**3), 32, 18.0),
            (10 * (1024**3), 5 * (1024**3), 100 * (1024**3), 8, 40.0),
            (20 * (1024**3), 10 * (1024**3), 200 * (1024**3), 10, 20.0),
            (40 * (1024**3), 20 * (1024**3), 400 * (1024**3), 20, 60.0),
            (50 * (1024**3), 25 * (1024**3), 500 * (1024**3), 16, 55.5),
            (70 * (1024**3), 35 * (1024**3), 700 * (1024**3), 24, 70.0),
            (80 * (1024**3), 40 * (1024**3), 800 * (1024**3), 32, 80.0),
            (90 * (1024**3), 45 * (1024**3), 900 * (1024**3), 36, 85.0),
            (100 * (1024**3), 50 * (1024**3), 1000 * (1024**3), 48, 95.0),
        ]
        for total_ram, used_ram, free_disk, cores, cpu_pct in test_cases:
            mock_vmem.return_value = VMem(total=total_ram, used=used_ram)
            mock_disk.return_value = DiskUsage(free=free_disk)
            mock_cpu_count.return_value = cores
            mock_cpu_percent.return_value = cpu_pct

            d = hd.HardwareDetector()
            d.get_computer_specs()
            oracle_res = independent_oracle_calculator(total_ram, used_ram, free_disk, cores, cpu_pct)
            self.assertEqual(d.hardware_profile, oracle_res)


if __name__ == "__main__":
    unittest.main()
