# R35-T041 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T041 (Issue #41)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T041

## Target Item
- Module: `Random Color Generator/RandColorGen.py`
- Target function: `GenerateRandomColorValue(min_val=0, max_val=255)`
- Anchors:
  - `RGBTextRect.center = (width // 2, height // 2 - 20)` (line 60 in pinned baseline)
  - `hexTextRect.center = (width // 2, height // 2 + 20)` (line 65 in pinned baseline)
- Precondition lines:
  - Lines 60 & 65 establish the UI canvas center offset positions.
  - Bounds `0 <= min_val <= max_val <= 255` define the valid 8-bit RGB integer space.

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Test Results and Evidence
1. Smallest valid input (`min_val = 0, max_val = 0` with `random.seed(42)`):
   - Input: `(0, 0)`
   - Expected Output: `(0, 0, 0)`
   - Actual Output: `(0, 0, 0)`
   - Result: PASS

2. Ordinary valid input (default `min_val = 0, max_val = 255` with `random.seed(42)`):
   - Input: `()` (default arguments `min_val=0, max_val=255`)
   - Expected Output: `(57, 12, 140)`
   - Actual Output: `(57, 12, 140)`
   - Result: PASS

3. Domain Boundary and Non-Mutation:
   - Upper boundary: `GenerateRandomColorValue(255, 255)` -> Expected: `(255, 255, 255)` | Actual: `(255, 255, 255)` -> PASS
   - Intermediate boundary: `GenerateRandomColorValue(128, 128)` -> Expected: `(128, 128, 128)` | Actual: `(128, 128, 128)` -> PASS
   - Non-mutation: module attributes and function references remain unmodified across repeated executions -> PASS

4. Unit Test Suite Execution:
   - Command: `python3 -m unittest "Random Color Generator/test_rand_color_gen.py"`
   - Ran 5 tests, 0 failures, 0 errors -> PASS

5. Negative / Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T041/check.py`
   - Output: `FAIL: Expected smallest result (-1, -1, -1), got (0, 0, 0)`
   - Exit code: 1
