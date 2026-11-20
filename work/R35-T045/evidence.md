# R35-T045 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T045 (Issue #45)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T045

## Target Item
- Module: `freelance-help-program/calc.py`
- Target Class/Method: `CalculateApp.calculate_payment`
- Source Anchors:
  - `def calculate_payment(self, file_path, pay_per_hour)` (Line 56 in original source)
  - `for row in range(2, sheet.max_row + 1):` (Line 62 in original source)
- Precondition lines:
  - Line 62: `for row in range(2, sheet.max_row + 1)` establishes data row requirement (`max_row >= 2`).
  - Lines 63-66: cell(row, 1) and cell(row, 2) contain valid time values.
  - Line 70: `pay_per_hour` is a positive numeric hourly rate.

## Dependency Seam Analysis
- External Dependencies:
  - Excel file I/O (`openpyxl.load_workbook` and `wb.save`).
  - GUI display (`tkinter.Tk`, `messagebox.showinfo`, `messagebox.showerror`).
- Dependency Seams Added:
  - `root=None` in `CalculateApp.__init__`: allows headless testing without opening a desktop GUI window.
  - `workbook=None` in `calculate_payment`: allows passing pre-loaded or mock workbooks without requiring filesystem writes.
  - `show_dialog=True` in `calculate_payment`: allows suppressing interactive messagebox dialogs in automated test environments while preserving GUI behavior for regular users.

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification Results
1. Smallest Valid Input (1 hour @ 50.0 Shekels/hr):
   - Input: 1 data row with `09:00:00` to `10:00:00`
   - Expected Output: `50.0`
   - Actual Output: `50.0`
   - Result: PASS

2. Ordinary Valid Input (7 hours @ 100.0 Shekels/hr):
   - Input: 2 data rows: 3 hours + 4 hours
   - Expected Output: `700.0`
   - Actual Output: `700.0`
   - Result: PASS

3. Repeatability and State Isolation Check:
   - Run 1 on Fixture A (1 hr @ 50.0): `50.0`
   - Intervening Run on Fixture B (8 hrs @ 50.0): `400.0`
   - Run 2 on Fixture A (1 hr @ 50.0): `50.0`
   - Assert Run 1 == Run 2 (no state contamination or memory leakage): PASS

4. Unit Test Suite Execution:
   - Command: `python3 -m unittest "freelance-help-program/test_calc.py"`
   - Ran 3 tests, 0 failures, 0 errors -> PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T045/check.py`
   - Output: `FAIL: Expected 999.0, got 50.0`
   - Exit code: 1
