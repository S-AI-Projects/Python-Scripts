# R35-T047 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T047 (Issue #47)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T047

## Target Item
- Module: `Password Strength Checker/main.py`
- Target Function: `main(password=None, predict_fn=None)`
- Source Anchors:
  - `def main():` (Line 3 in original source)
  - `password_to_test = input(...)` (Line 4 in original source)
  - `print(f"Password strength classification: {predicted_class} / 2")` (Line 6 in original source)
- Precondition lines:
  - Line 4 establishes password string input acquisition.
  - Line 5 establishes prediction inference returning an integer class.
  - Line 6 establishes printed classification string format.

## Worked Examples and Decisive State Transitions
1. Input Acquisition:
   Password string received via argument or `input()`.
2. Prediction Inference:
   `predict_fn(password)` computes feature extraction and yields categorical class index in `{0, 1, 2}`.
3. Formatted Display & Return:
   Prints `"Password strength classification: {predicted_class} / 2"` and returns the integer class.

- Worked Example 1 (Smallest Valid Input: `"a"`):
  - Input: `password="a"`
  - Intermediate Transition: `predict_fn("a")` -> `0`
  - Displayed Output: `"Password strength classification: 0 / 2"`
  - Return Value: `0`
- Worked Example 2 (Ordinary Valid Input: `"MyP@ssw0rd!2026"`):
  - Input: `password="MyP@ssw0rd!2026"`
  - Intermediate Transition: `predict_fn("MyP@ssw0rd!2026")` -> `2`
  - Displayed Output: `"Password strength classification: 2 / 2"`
  - Return Value: `2`

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification Results
1. Smallest Valid Input Execution:
   - Evaluated `main(password="a", predict_fn=lambda p: 0)`
   - Class: `0`, Output: `"Password strength classification: 0 / 2"`
   - Result: PASS

2. Ordinary Valid Input Execution:
   - Evaluated `main(password="MyP@ssw0rd!2026", predict_fn=lambda p: 2)`
   - Class: `2`, Output: `"Password strength classification: 2 / 2"`
   - Result: PASS

3. Interactive Stdin Compatibility:
   - Evaluated `main()` with mocked `input("moderate123")`
   - Class: `1`, Output: `"Password strength classification: 1 / 2"`
   - Result: PASS

4. Unit Test Suite Execution:
   - Command: `python3 -m unittest "Password Strength Checker/test_main.py"`
   - Ran 3 tests, 0 failures, 0 errors -> PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T047/check.py`
   - Output: `FAIL: Expected 'Password strength classification: 999 / 2', got 'Password strength classification: 0 / 2'`
   - Exit code: 1
