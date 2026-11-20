# R35-T042 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T042 (Issue #42)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T042

## Target Item
- Module: `Fake Profile/FakeProfile.py`
- Target item: `generate_fake_profiles(num_profiles: int)`
- Anchor: `profiles = []` (Line 19 in original source)
- Precondition lines:
  - Line 19 establishes anchor `profiles = []`.
  - Lines 77-78 establish the boundary condition `if num_profiles < 1: raise ValueError("Number of profiles must be greater than 0.")`.

## Boundary Table

| Category | Input Condition | Expected Behavior | Source Line Reference |
| :--- | :--- | :--- | :--- |
| Valid Interior | `num_profiles = 3` | Returns list of 3 profile dictionaries | lines 20-33 |
| Valid Boundary (Min Valid) | `num_profiles = 1` | Smallest valid input, returns list with exactly 1 profile | lines 20-33 |
| Unsupported Boundary (Zero) | `num_profiles = 0` | Raises `ValueError("Number of profiles must be greater than 0.")` | lines 77-78 |
| Unsupported (Negative) | `num_profiles = -1` | Raises `ValueError("Number of profiles must be greater than 0.")` | lines 77-78 |

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification Results
1. Smallest valid input (`num_profiles = 1`):
   - Input: `1`
   - Expected Output: List of length 1 containing valid profile dict with expected keys.
   - Actual Output: List of length 1 with matching keys and mocked data.
   - Result: PASS

2. Ordinary valid input (`num_profiles = 3`):
   - Input: `3`
   - Expected Output: List of length 3 containing valid profile dicts.
   - Actual Output: List of length 3.
   - Result: PASS

3. Unsupported Boundary Values (`num_profiles = 0` and `num_profiles = -1`):
   - Both raise `ValueError("Number of profiles must be greater than 0.")`.
   - Result: PASS

4. Unit Test Suite Execution:
   - Command: `python3 -m unittest "Fake Profile/test_fake_profile.py"`
   - Ran 5 tests, 0 failures, 0 errors -> PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T042/check.py`
   - Output: `FAIL: Expected profile count 999, got 1`
   - Exit code: 1
