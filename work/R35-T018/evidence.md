# R35-T018 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T018 (Issue #18)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T018

## Target Item
- Module: `File Encryption Decryption/fileEncryptDecrypt.py`
- Target function: `encryptFile` and `decryptFile`
- Preconditions established at: `File Encryption Decryption/fileEncryptDecrypt.py`:
  - `pyAesCrypt` import (line 9)
  - `sys` import (line 10)
  - `encryptFile` contract (line 17)
  - `decryptFile` contract (line 53)

## Failure Contract Specification

| Failure Condition | Input State | Expected Exception | State / Resource Invariant | Source Line |
| :--- | :--- | :--- | :--- | :--- |
| Missing File | Non-existent path string | `FileNotFoundError` | No `.aes` file created or modified | `line 37` |
| Empty Password | `password = ""` | `ValueError` | Source and destination unchanged | `line 35` |
| Invalid Password Type | `password = None` | `ValueError` | Source and destination unchanged | `line 35` |
| Empty Filename | `filename = ""` | `ValueError` | No filesystem side effects | `line 33` |
| Interrupted Encryption | Mid-flight I/O failure | Propagates exception | Partial `.aes` file deleted immediately | `lines 47-51` |

## Verification Results
1. Smallest valid input (empty 0-byte file):
   - Input: 0-byte file, password `"p"`
   - Expected Output: `<path>.aes` created, round-trips back to 0 bytes
   - Actual Output: Matches expected
   - Result: PASS

2. Ordinary valid input (standard 43-byte text file):
   - Input: text file, password `"SecretPass!"`
   - Expected Output: `<path>.aes` created, round-trips to exact text
   - Actual Output: Matches expected
   - Result: PASS

3. Failure Coverage:
   - `FileNotFoundError` asserted and verified: PASS
   - `ValueError` for invalid password asserted: PASS
   - `ValueError` for empty filename asserted: PASS
   - Partial file cleanup on simulated failure asserted: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T018/check.py`
   - Output: `FAIL: Smallest input mismatch: expected 'WRONG_PATH', got '...'`
   - Exit code: 1
