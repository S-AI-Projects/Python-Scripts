# R35-T050 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T050 (Issue #50)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T050

## Target Item
- Module: `Virtual Painter/virtual_paint_app.py`
- Target Function: `getTool(x)`
- Source Anchors:
  - `max_x, max_y = 250+ml, 50` (Line 8 in original source)
  - `prevx, prevy = 0,0` (Line 14 in original source)
  - `def getTool(x):` (Line 17 in original source)
- Precondition lines:
  - Line 7: `ml = 150` establishes margin offset.
  - Line 8: `max_x = 250 + ml = 400`, `max_y = 50`.
  - Line 75: `if x < max_x and y < max_y and x > ml:` establishes toolbar coordinate domain `150 < x < 400`.

## Mutation Testing Design
- **Plausible One-Line Mistake**: An off-by-one boundary comparison replacing strict inequality `<` with `<=` at line 18:
  ```python
  # Original:
  if x < 50 + ml:  # (x < 200) -> returns "line"
  # Mutant:
  if x <= 50 + ml:  # (x <= 200) -> returns "line"
  ```
- **Protected Semantic Condition**: Precise boundary demarcation between adjacent toolbar items (`line` and `rectangle` at coordinate boundary `x = 200`).
- **Minimal Differentiating Input**: `x = 200` (`50 + ml`).
- **Differential Behavior**:
  - Original implementation evaluates `200 < 200` as `False`, proceeding to `elif x < 100 + ml` and returning `"rectangle"` (PASS).
  - Mutated implementation evaluates `200 <= 200` as `True`, returning `"line"` (FAILS assertion `self.assertEqual(getTool(200), "rectangle")`).
  - Confirms the regression test detects plausible off-by-one boundary bugs and protects semantic tool boundaries.

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification Results
1. Source Anchors:
   - `max_x, max_y = 250+ml, 50`: `(400, 50)` (PASS)
   - `prevx, prevy = 0,0`: `(0, 0)` (PASS)

2. Smallest Valid Input (`x = 151`):
   - Expected Output: `"line"`
   - Actual Output: `"line"`
   - Result: PASS

3. Ordinary Valid Input (`x = 275`):
   - Expected Output: `"draw"`
   - Actual Output: `"draw"`
   - Result: PASS

4. Boundary Tool Mapping Verification:
   - `x = 199` -> `"line"` (PASS)
   - `x = 200` -> `"rectangle"` (PASS)
   - `x = 249` -> `"rectangle"` (PASS)
   - `x = 250` -> `"draw"` (PASS)
   - `x = 299` -> `"draw"` (PASS)
   - `x = 300` -> `"circle"` (PASS)
   - `x = 349` -> `"circle"` (PASS)
   - `x = 350` -> `"erase"` (PASS)

5. Mutation Detection Verification:
   - Original `getTool(200)` -> `"rectangle"` (PASS)
   - Mutant `mutant_getTool(200)` -> `"line"` (FAILS test assertion as expected, PASS)

6. Unit Test Suite Execution:
   - Command: `python3 -m unittest "Virtual Painter/test_virtual_paint_app.py"`
   - Ran 5 tests, 0 failures, 0 errors -> PASS

7. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T050/check.py`
   - Output: `FAIL: Expected WRONG_TOOL, got line`
   - Exit code: 1
