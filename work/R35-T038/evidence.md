# R35-T038 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T038 (Issue #38)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T038

## Target Item
- Module: `Star Pattern/starPattern.py`
- Target Function: `starPattern(n)`
- Precondition lines: Line 18 (`starPattern` entry point), Lines 20-24 (loop bounds `range(1, n+1)`)

## Failure / Absent-Result Branch Semantics
- In mathematical and function contracts over the integers, `starPattern` has a total contract where row counts `n <= 0` yield an empty/absent pattern (zero rows printed and empty string returned).
- Tested branch: Lines 20-24 (`for i in range(1, n + 1):`). When `n = 0` (smallest non-positive input) or `n < 0`, the range evaluates to empty, bypassing the loop completely.
- Verification ensures that caller-owned state remains completely uncorrupted and that subsequent ordinary positive calls (`n = 2`) succeed immediately.

## Tool Versions
- Python: 3.15.2
- OS: macOS (Darwin)

## Verification Results
1. Smallest Valid Positive Input (`n = 1`):
   - Expected Output: `"* \n"`
   - Actual Output: `"* \n"`
   - Result: PASS

2. Ordinary Valid Input (`n = 3`):
   - Expected Output: `"* \n* * \n* * * \n"`
   - Actual Output: `"* \n* * \n* * * \n"`
   - Result: PASS

3. Absent-Result / Non-Positive Inputs (`n = 0` and `n = -5`):
   - Expected Output: `""`
   - Actual Output: `""`
   - Result: PASS

4. Recovery (Successful Call Following Absent Result):
   - Triggered `n = 0`, followed by `n = 2` -> Output: `"* \n* * \n"`
   - Result: PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T038/check.py`
   - Output: `FAIL: Expected 'WRONG_STARS', got ''`
   - Exit code: 1
