import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock faker before importing FakeProfile to enable testing without external I/O or packages
if "faker" not in sys.modules:
    mock_faker_mod = MagicMock()
    mock_fake_instance = MagicMock()
    mock_fake_instance.locales = ['it_IT', 'en_US', 'ja_JP']
    mock_fake_instance.name.return_value = "Jane Doe"
    mock_fake_instance.email.return_value = "janedoe@example.com"
    mock_fake_instance.ssn.return_value = "987-65-4321"
    mock_fake_instance.address.return_value = "456 Market St, San Francisco, CA"
    mock_fake_instance.latitude.return_value = 37.789
    mock_fake_instance.longitude.return_value = -122.401
    mock_fake_instance.url.return_value = "https://janedoe.org"
    mock_faker_mod.Faker.return_value = mock_fake_instance
    sys.modules["faker"] = mock_faker_mod

# Ensure Fake Profile module directory is in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import FakeProfile as fp


class TestFakeProfileBoundaries(unittest.TestCase):
    """Boundary and regression tests for generate_fake_profiles."""

    def test_smallest_valid_input(self):
        """
        Test smallest supported valid input: num_profiles = 1.
        Precondition: num_profiles >= 1 established by lines 77-78.
        Anchor: profiles = [] established by line 19.
        """
        result = fp.generate_fake_profiles(1)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

        expected_keys = {
            "Locale", "Name", "Email", "SSN", "Address", "Latitude", "Longitude", "URL"
        }
        self.assertEqual(set(result[0].keys()), expected_keys)
        self.assertEqual(result[0]["Locale"], ['it_IT', 'en_US', 'ja_JP'])
        self.assertEqual(result[0]["Name"], "Jane Doe")
        self.assertEqual(result[0]["Email"], "janedoe@example.com")
        self.assertEqual(result[0]["SSN"], "987-65-4321")

    def test_ordinary_valid_input(self):
        """
        Test interior valid input: num_profiles = 3.
        """
        result = fp.generate_fake_profiles(3)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        for profile in result:
            self.assertEqual(profile["Name"], "Jane Doe")
            self.assertEqual(profile["Email"], "janedoe@example.com")

    def test_unsupported_boundary_zero(self):
        """
        Test boundary unsupported input: num_profiles = 0.
        Must raise ValueError with the exact contract message from line 78.
        """
        with self.assertRaises(ValueError) as ctx:
            fp.generate_fake_profiles(0)
        self.assertIn("Number of profiles must be greater than 0.", str(ctx.exception))

    def test_unsupported_boundary_negative(self):
        """
        Test unsupported input: negative numbers (e.g., -1, -10).
        Must raise ValueError matching line 78.
        """
        with self.assertRaises(ValueError) as ctx:
            fp.generate_fake_profiles(-1)
        self.assertIn("Number of profiles must be greater than 0.", str(ctx.exception))

    def test_no_observable_mutation(self):
        """
        Ensure generate_fake_profiles does not mutate external references or module functions.
        """
        initial_func = fp.generate_fake_profiles
        initial_fake = fp.fake
        res = fp.generate_fake_profiles(2)
        self.assertEqual(len(res), 2)
        self.assertIs(fp.generate_fake_profiles, initial_func)
        self.assertIs(fp.fake, initial_fake)


if __name__ == "__main__":
    unittest.main()
