import os
import sys
import tempfile
import unittest

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

from cryptography.fernet import Fernet
import pwd_mgmr as pm_module


class TestPasswordManagerStrengthened(unittest.TestCase):
    """
    Focused mutation-resistant tests for PasswordManager (pwd_mgmr.py).
    Precondition source lines:
      - pwd_mgmr.py:1 establishes Fernet import
      - pwd_mgmr.py:5 establishes PasswordManager
      - pwd_mgmr.py:9 establishes self.pwd_dict = {} anchor
      - pwd_mgmr.py:27 establishes add_password
      - pwd_mgmr.py:36 establishes get_password
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_anchor_initialization(self):
        # Verify source anchor: self.pwd_dict = {}
        pm = pm_module.PasswordManager()
        self.assertEqual(pm.pwd_dict, {})
        self.assertIsNone(pm.key)
        self.assertIsNone(pm.pwd_file)

    def test_smallest_valid_input(self):
        # Smallest valid input: single character site and password
        pm = pm_module.PasswordManager()
        pm.add_password("a", "b")
        self.assertEqual(pm.get_password("a"), "b")
        self.assertEqual(pm.pwd_dict, {"a": "b"})
        self.assertEqual(pm.get_sites(), ["a"])

    def test_ordinary_valid_input_and_file_persistence(self):
        # Ordinary input with Fernet encryption/decryption round-trip
        key_path = os.path.join(self.temp_dir.name, "secret.key")
        pwd_path = os.path.join(self.temp_dir.name, "passwords.txt")

        pm1 = pm_module.PasswordManager()
        pm1.create_key(key_path)
        self.assertTrue(os.path.exists(key_path))

        pm1.create_pwd_file(pwd_path)
        pm1.add_password("github.com", "S3cure_P@ssw0rd!")
        pm1.add_password("google.com", "G00gl3-Auth#2026")

        self.assertEqual(pm1.get_password("github.com"), "S3cure_P@ssw0rd!")
        self.assertEqual(pm1.get_password("google.com"), "G00gl3-Auth#2026")

        # Load into fresh second manager instance
        pm2 = pm_module.PasswordManager()
        pm2.load_key(key_path)
        pm2.load_pwd_file(pwd_path)

        self.assertEqual(pm2.get_password("github.com"), "S3cure_P@ssw0rd!")
        self.assertEqual(pm2.get_password("google.com"), "G00gl3-Auth#2026")
        self.assertEqual(sorted(pm2.get_sites()), ["github.com", "google.com"])

    def test_create_pwd_file_with_init_values(self):
        key_path = os.path.join(self.temp_dir.name, "init.key")
        pwd_path = os.path.join(self.temp_dir.name, "init_pwd.txt")

        pm = pm_module.PasswordManager()
        pm.create_key(key_path)
        pm.create_pwd_file(pwd_path, init_values={"aws.amazon.com": "RootPass@99"})

        self.assertEqual(pm.get_password("aws.amazon.com"), "RootPass@99")
        self.assertIn("aws.amazon.com", pm.pwd_dict)

    def test_mutation_detection_case_sensitivity(self):
        # Proves that test catches plausible mutation (e.g. lowercase mutation or truncation)
        pm = pm_module.PasswordManager()
        raw_pwd = "MixedCasePassword!#123"
        pm.add_password("portal.nst.edu", raw_pwd)

        retrieved = pm.get_password("portal.nst.edu")
        self.assertEqual(retrieved, raw_pwd)
        # Explicit assertion that catches casing or truncation mutants
        self.assertNotEqual(retrieved, raw_pwd.lower())
        self.assertNotEqual(retrieved, raw_pwd[:-1])


if __name__ == "__main__":
    unittest.main()
