import unittest
import random
import sys
import os

# Ensure module is accessible
sys.path.insert(0, os.path.dirname(__file__))
import PasswordGenerator as pg


class TestPasswordGenerator(unittest.TestCase):
    def setUp(self):
        self.initial_characters = list(pg.characters)

    def tearDown(self):
        # Assert no observable mutation on characters anchor
        self.assertEqual(pg.characters, self.initial_characters, "characters list should not be mutated")

    def test_smallest_valid_input(self):
        # Line 4 establishes: characters = ['@', '#', '$', '%', '&', '?']
        # Line 8-24 establishes smallest valid length is 4 (2 letters, 1 number, 1 symbol)
        random.seed(42)
        pwd, cap, low, num, sym = pg.generate_password(4)
        expected_pwd = 'Hh2?'
        self.assertEqual(pwd, expected_pwd)
        self.assertEqual(cap, 1)
        self.assertEqual(low, 1)
        self.assertEqual(num, 1)
        self.assertEqual(sym, 1)
        self.assertEqual(len(pwd), 4)
        self.assertEqual(cap + low + num + sym, 4)

    def test_ordinary_valid_input(self):
        random.seed(42)
        pwd, cap, low, num, sym = pg.generate_password(12)
        expected_pwd = 'HHe1??&@&%@@'
        self.assertEqual(pwd, expected_pwd)
        self.assertEqual(cap, 2)
        self.assertEqual(low, 1)
        self.assertEqual(num, 1)
        self.assertEqual(sym, 8)
        self.assertEqual(len(pwd), 12)
        self.assertEqual(cap + low + num + sym, 12)

    def test_domain_boundary_and_non_mutation(self):
        # Test repeated boundary calls and verify characters immutability
        for _ in range(5):
            pwd, cap, low, num, sym = pg.generate_password(4)
            self.assertEqual(len(pwd), 4)
            self.assertGreaterEqual(cap, 1)
            self.assertGreaterEqual(low, 1)
            self.assertGreaterEqual(num, 1)
            self.assertGreaterEqual(sym, 1)
        self.assertEqual(pg.characters, ['@', '#', '$', '%', '&', '?'])


if __name__ == '__main__':
    unittest.main()
