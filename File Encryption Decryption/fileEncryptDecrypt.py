# This is code for File Encryption Decryption Using AES Algorithms

# Advanced Encryption Standard (AES) is a specification for the encryption of electronic data established by the U.S National Institute of Standards and Technology (NIST) in 2001. AES is widely used today as it is a much stronger than DES and triple DES despite being harder to implement.

# pyAesCrypt is a file encryption module that uses AES256-CBC to encrypt/decrypt files and binary streams. Install pyAesCrypt as follows: pip3 install pyAesCrypt.

import os
import sys

try:
    import pyAesCrypt
except ImportError:
    pyAesCrypt = None


def encryptFile(filename: str, password: str, buffer_size: int = 64 * 1024) -> str:
    """
    Encrypt a file using AES256-CBC via pyAesCrypt.

    Failure & Boundary Contract:
    - Precondition: filename must be an existing valid file path (source line 13).
    - Precondition: password must be a non-empty string.
    - If filename is empty or not string: raises ValueError.
    - If file does not exist: raises FileNotFoundError.
    - If password is empty or not string: raises ValueError.
    - On failure: ensures no partial or corrupt .aes output file is leaked.
    - Returns: target encrypted file path string (<filename>.aes).
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty path string")
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Source file not found: {filename}")

    if pyAesCrypt is None:
        raise RuntimeError("pyAesCrypt module is not installed")

    out_file = filename + ".aes"
    try:
        pyAesCrypt.encryptFile(filename, out_file, password, buffer_size)
        print("File Encryption successfully done.")
        return out_file
    except Exception:
        # Prevent leaking partial corrupt files on failure
        if os.path.exists(out_file):
            try:
                os.remove(out_file)
            except OSError:
                pass
        raise


def decryptFile(filename: str, password: str, buffer_size: int = 64 * 1024) -> str:
    """
    Decrypt an AES-encrypted file via pyAesCrypt.
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty path string")
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")

    aes_file = filename if filename.endswith(".aes") else filename + ".aes"
    out_file = filename[:-4] if filename.endswith(".aes") else filename

    if not os.path.exists(aes_file):
        raise FileNotFoundError(f"Encrypted file not found: {aes_file}")

    if pyAesCrypt is None:
        raise RuntimeError("pyAesCrypt module is not installed")

    try:
        pyAesCrypt.decryptFile(aes_file, out_file, password, buffer_size)
        print("File Decryption successfully done.")
        return out_file
    except Exception:
        if os.path.exists(out_file):
            try:
                os.remove(out_file)
            except OSError:
                pass
        raise


def main():
    if len(sys.argv) < 3:
        print("Usage: python fileEncryptDecrypt.py <filename> <password>")
        return
    encryptFile(sys.argv[1], sys.argv[2])
    decryptFile(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()
