# R35-T031 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T031 (Issue #31)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T031

## Target Item
- Module: `Password Generator/PasswordGenerator.py`
- Target function: `generate_password(pass_len)`
- Anchor: `characters = ['@', '#', '$', '%', '&', '?']` (Line 4)
- Precondition lines: Line 4 (characters anchor), Lines 15-23 (ensures >=2 letters, >=1 number, >=1 symbol, establishing pass_len >= 4 as minimum supported input), Line 79 (main validation for pass_len < 4)

## Tool Versions
- Python: 3.15.2
- OS: macOS (Darwin)

## Test Results and Evidence
1. Smallest valid input (`pass_len = 4` with `random.seed(42)`):
   - Input: `4`
   - Expected Output: `('Hh2?', 1, 1, 1, 1)`
   - Actual Output: `('Hh2?', 1, 1, 1, 1)`
   - Result: PASS

2. Ordinary valid input (`pass_len = 12` with `random.seed(42)`):
   - Input: `12`
   - Expected Output: `('HHe1??&@&%@@', 2, 1, 1, 8)`
   - Actual Output: `('HHe1??&@&%@@', 2, 1, 1, 8)`
   - Result: PASS

3. Domain Boundary and Non-Mutation:
   - Repeated generation across 20 iterations verifying `characters` list is never mutated and stays `['@', '#', '$', '%', '&', '?']`.
   - Result: PASS

4. Negative / Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T031/check.py`
   - Output: `FAIL: Expected password 'WRONG_OUTPUT', got 'Hh2?'`
   - Exit code: 1
