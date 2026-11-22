import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parent / "hardware_detector.py"
SPEC = importlib.util.spec_from_file_location("hardware_detector", MODULE_PATH)
hardware_detector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hardware_detector)


GIB = 1024 ** 3


def independent_reference(total_ram_bytes, used_ram_bytes, free_disk_bytes,
                          cpu_cores, cpu_usage_percent):
    return {
        "ram_total_gb": round(total_ram_bytes / GIB, 2),
        "ram_used_gb": round(used_ram_bytes / GIB, 2),
        "available_diskspace_gb": round(free_disk_bytes / GIB, 2),
        "cpu_cores": cpu_cores,
        "cpu_usage_percent": cpu_usage_percent,
    }


class TestHardwareDetector(unittest.TestCase):
    def test_smallest_valid_input(self):
        """Source precondition: hardware_profile is initialized at line 13."""
        detector = hardware_detector.HardwareDetector()

        with patch.object(hardware_detector.psutil, "virtual_memory",
                          return_value=type("Memory", (), {"total": 1 * GIB, "used": 0})()), \
                patch.object(hardware_detector.psutil, "disk_usage",
                           return_value=type("Disk", (), {"free": 1 * GIB})()), \
                patch.object(hardware_detector.psutil, "cpu_count", return_value=1), \
                patch.object(hardware_detector.psutil, "cpu_percent", return_value=0.0):
            detector.get_computer_specs()

        expected = {
            "ram_total_gb": 1.0,
            "ram_used_gb": 0.0,
            "available_diskspace_gb": 1.0,
            "cpu_cores": 1,
            "cpu_usage_percent": 0.0,
        }
        self.assertEqual(detector.hardware_profile, expected)

    def test_ordinary_valid_input(self):
        """Source precondition: get_computer_specs writes the five keys at lines 48-52."""
        detector = hardware_detector.HardwareDetector()

        with patch.object(hardware_detector.psutil, "virtual_memory",
                          return_value=type("Memory", (), {
                              "total": 16 * GIB,
                              "used": 8 * GIB,
                          })()), \
                patch.object(hardware_detector.psutil, "disk_usage",
                           return_value=type("Disk", (), {"free": 100 * GIB})()), \
                patch.object(hardware_detector.psutil, "cpu_count", return_value=8), \
                patch.object(hardware_detector.psutil, "cpu_percent", return_value=15.5):
            detector.get_computer_specs()

        expected = {
            "ram_total_gb": 16.0,
            "ram_used_gb": 8.0,
            "available_diskspace_gb": 100.0,
            "cpu_cores": 8,
            "cpu_usage_percent": 15.5,
        }
        self.assertEqual(detector.hardware_profile, expected)

    def test_profile_is_updated_in_place_and_has_explicit_key_order(self):
        """The dictionary at line 13 must remain one object and receive keys in lines 48-52."""
        detector = hardware_detector.HardwareDetector()
        original_profile = detector.hardware_profile
        original_profile["gpu_name"] = "Existing GPU"

        with patch.object(hardware_detector.psutil, "virtual_memory",
                          return_value=type("Memory", (), {"total": 4 * GIB, "used": 2 * GIB})()), \
                patch.object(hardware_detector.psutil, "disk_usage",
                           return_value=type("Disk", (), {"free": 20 * GIB})()), \
                patch.object(hardware_detector.psutil, "cpu_count", return_value=4), \
                patch.object(hardware_detector.psutil, "cpu_percent", return_value=25.0):
            detector.get_computer_specs()

        self.assertIs(detector.hardware_profile, original_profile)
        self.assertEqual(detector.hardware_profile["gpu_name"], "Existing GPU")
        expected_order = [
            "gpu_name",
            "ram_total_gb",
            "ram_used_gb",
            "available_diskspace_gb",
            "cpu_cores",
            "cpu_usage_percent",
        ]
        self.assertEqual(list(detector.hardware_profile.keys()), expected_order)

    def test_25_configurations_against_independent_reference(self):
        """These 25 literals use bytes as input and an independent division reference."""
        configurations = [
            (1 * GIB, 0, 1 * GIB, 1, 0.0),
            (2 * GIB, 1 * GIB, 10 * GIB, 2, 5.0),
            (3 * GIB, 1 * GIB, 15 * GIB, 2, 7.5),
            (4 * GIB, 2 * GIB, 20 * GIB, 4, 10.0),
            (5 * GIB, 2 * GIB, 25 * GIB, 4, 12.5),
            (6 * GIB, 3 * GIB, 30 * GIB, 6, 15.0),
            (7 * GIB, 3 * GIB, 35 * GIB, 6, 17.5),
            (8 * GIB, 4 * GIB, 40 * GIB, 8, 20.0),
            (9 * GIB, 4 * GIB, 45 * GIB, 8, 22.5),
            (10 * GIB, 5 * GIB, 50 * GIB, 10, 25.0),
            (11 * GIB, 5 * GIB, 55 * GIB, 10, 27.5),
            (12 * GIB, 6 * GIB, 60 * GIB, 12, 30.0),
            (13 * GIB, 6 * GIB, 65 * GIB, 12, 32.5),
            (14 * GIB, 7 * GIB, 70 * GIB, 14, 35.0),
            (15 * GIB, 7 * GIB, 75 * GIB, 14, 37.5),
            (16 * GIB, 8 * GIB, 80 * GIB, 16, 40.0),
            (17 * GIB, 8 * GIB, 85 * GIB, 16, 42.5),
            (18 * GIB, 9 * GIB, 90 * GIB, 18, 45.0),
            (20 * GIB, 10 * GIB, 100 * GIB, 20, 50.0),
            (24 * GIB, 12 * GIB, 120 * GIB, 24, 55.5),
            (32 * GIB, 16 * GIB, 160 * GIB, 32, 65.0),
            (48 * GIB, 24 * GIB, 240 * GIB, 48, 75.5),
            (64 * GIB, 32 * GIB, 320 * GIB, 64, 85.0),
            (96 * GIB, 48 * GIB, 480 * GIB, 96, 95.5),
            (128 * GIB, 64 * GIB, 640 * GIB, 128, 99.9),
        ]

        for total_ram, used_ram, free_disk, cores, usage in configurations:
            with self.subTest(total_ram=total_ram):
                detector = hardware_detector.HardwareDetector()
                with patch.object(hardware_detector.psutil, "virtual_memory",
                                  return_value=type("Memory", (), {
                                      "total": total_ram,
                                      "used": used_ram,
                                  })()), \
                        patch.object(hardware_detector.psutil, "disk_usage",
                                     return_value=type("Disk", (), {"free": free_disk})()), \
                        patch.object(hardware_detector.psutil, "cpu_count", return_value=cores), \
                        patch.object(hardware_detector.psutil, "cpu_percent", return_value=usage):
                    detector.get_computer_specs()

                expected = independent_reference(
                    total_ram, used_ram, free_disk, cores, usage
                )
                self.assertEqual(detector.hardware_profile, expected)


if __name__ == "__main__":
    unittest.main()
