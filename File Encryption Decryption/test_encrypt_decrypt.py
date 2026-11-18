import os
import sys
import tempfile
import unittest
from unittest.mock import patch

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

import fileEncryptDecrypt as fed


class TestFileEncryptDecryptFailures(unittest.TestCase):
    """
    Focused unit tests covering failure and boundary behavior for encryptFile (fileEncryptDecrypt.py).
    Precondition source lines:
      - fileEncryptDecrypt.py:9 establishes pyAesCrypt import
      - fileEncryptDecrypt.py:10 establishes sys import
      - fileEncryptDecrypt.py:17 establishes encryptFile contract
      - fileEncryptDecrypt.py:53 establishes decryptFile contract
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_smallest_valid_input_empty_file(self):
        src_path = os.path.join(self.temp_dir.name, "tiny.txt")
        with open(src_path, "wb") as f:
            f.write(b"")

        aes_path = fed.encryptFile(src_path, "p")
        self.assertTrue(os.path.exists(aes_path))
        self.assertTrue(aes_path.endswith(".aes"))

        # Clean decrypt and verify original 0 bytes
        os.remove(src_path)
        fed.decryptFile(aes_path, "p")
        self.assertTrue(os.path.exists(src_path))
        with open(src_path, "rb") as f:
            self.assertEqual(f.read(), b"")

    def test_ordinary_valid_input(self):
        src_path = os.path.join(self.temp_dir.name, "ordinary.txt")
        content = b"Ordinary test file data for AES encryption verification."
        with open(src_path, "wb") as f:
            f.write(content)

        aes_path = fed.encryptFile(src_path, "StrongPassword!456")
        self.assertTrue(os.path.exists(aes_path))

        os.remove(src_path)
        fed.decryptFile(aes_path, "StrongPassword!456")
        self.assertTrue(os.path.exists(src_path))
        with open(src_path, "rb") as f:
            self.assertEqual(f.read(), content)

    def test_failure_nonexistent_file(self):
        missing = os.path.join(self.temp_dir.name, "nonexistent.txt")
        expected_aes = missing + ".aes"

        with self.assertRaises(FileNotFoundError):
            fed.encryptFile(missing, "pass")

        self.assertFalse(os.path.exists(expected_aes), "Must not create or leak .aes file for missing input")

    def test_failure_empty_or_invalid_password(self):
        src_path = os.path.join(self.temp_dir.name, "valid.txt")
        with open(src_path, "w") as f:
            f.write("content")

        with self.assertRaises(ValueError):
            fed.encryptFile(src_path, "")
        with self.assertRaises(ValueError):
            fed.encryptFile(src_path, None)

        self.assertFalse(os.path.exists(src_path + ".aes"))

    def test_failure_empty_or_invalid_filename(self):
        with self.assertRaises(ValueError):
            fed.encryptFile("", "password")
        with self.assertRaises(ValueError):
            fed.encryptFile(None, "password")

    def test_failure_cleans_up_partial_file_on_error(self):
        src_path = os.path.join(self.temp_dir.name, "abort_test.txt")
        with open(src_path, "w") as f:
            f.write("some data")
        target_aes = src_path + ".aes"

        def failing_encrypt(src, dst, pwd, buf):
            with open(dst, "w") as pf:
                pf.write("partial corrupt data")
            raise IOError("Simulated disk error during encryption")

        with patch.object(fed.pyAesCrypt, "encryptFile", side_effect=failing_encrypt):
            with self.assertRaises(IOError):
                fed.encryptFile(src_path, "pass")

        self.assertFalse(os.path.exists(target_aes), "Partial file must be cleaned up on failure")


if __name__ == "__main__":
    unittest.main()
