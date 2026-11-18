# R35-T013 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T013 (Issue #13)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T013

## Target Item
- Module: `TCP Chat Server/server.py`
- Target function: `main` and `handle_client_connection`
- Preconditions established at: `TCP Chat Server/server.py` lines 3-7:
  - `IP = '0.0.0.0'` (line 3)
  - `PORT = 3000` (line 4)
  - `handle_client_connection` (line 7)

## Oracle Specification
An independent reference function `independent_oracle_session(raw_bytes, reply_str)` calculates:
- Decoded incoming UTF-8 string: `raw_bytes.decode('utf-8')`
- Sent UTF-8 encoded response bytes: `reply_str.encode('utf-8')`
- Transaction tuple: `(address, decoded, reply_str)`

The test suite enumerates 25 distinct synthetic inputs (empty string, symbols, unicode characters, numbers, newlines, binary-like sequences) and cross-checks the server's output against the oracle calculation.

## Verification Results
1. Smallest valid input (`b""`, `""`):
   - Input: empty payload bytes and empty response
   - Expected Output: `("", "")`
   - Actual Output: `("", "")`
   - Result: PASS

2. Ordinary valid input (`b"Hello from client"`, `"Hello from server"`):
   - Input: standard greeting messages
   - Expected Output: `("Hello from client", "Hello from server")`
   - Actual Output: `("Hello from client", "Hello from server")`
   - Result: PASS

3. 25-Case Oracle Cross-Check:
   - 25 distinct payloads verified against independent oracle
   - All 25 match exactly
   - Result: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T013/check.py`
   - Output: `FAIL: Smallest input mismatch: expected 'WRONG_VALUE', got ''`
   - Exit code: 1
