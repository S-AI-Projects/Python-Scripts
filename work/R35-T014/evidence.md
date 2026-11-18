# R35-T014 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T014 (Issue #14)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T014

## Target Item
- Module: `Digital Clock/DigitalClock.py`
- Target function: `format_time` and `time`
- Preconditions established at: `Digital Clock/DigitalClock.py`:
  - `strftime` import (line 2)
  - `TIME_FORMAT = '%H: %M: %S %p'` (line 4)
  - `format_time` (line 7)
  - `time` (line 27)

## Invariant Formulation
1. **Length and Type Invariant**: The formatted time output string is always of type `str` and length exactly 13 characters (`'HH: MM: SS PP'`).
2. **Structural Pattern Invariant**: For every valid `time.struct_time`, the string matches regular expression `^(\d{2}): (\d{2}): (\d{2}) (AM|PM)$`.
3. **Range Preservation**:
   - `00 <= int(HH) <= 23`
   - `00 <= int(MM) <= 59`
   - `00 <= int(SS) <= 59`
4. **Period Partition**:
   - For `00 <= int(HH) < 12`, period must equal `'AM'`.
   - For `12 <= int(HH) <= 23`, period must equal `'PM'`.

## Verification Results
1. Smallest valid input (`midnight`, 00:00:00 AM):
   - Input: `time.struct_time(2026, 1, 1, 0, 0, 0, ...)`
   - Expected Output: `"00: 00: 00 AM"`
   - Actual Output: `"00: 00: 00 AM"`
   - Result: PASS

2. Ordinary valid input (`afternoon`, 14:30:45 PM):
   - Input: `time.struct_time(2026, 11, 18, 14, 30, 45, ...)`
   - Expected Output: `"14: 30: 45 PM"`
   - Actual Output: `"14: 30: 45 PM"`
   - Result: PASS

3. Domain-Wide Invariant Property Check:
   - 96 distinct synthetic time fixtures evaluated across 24 hours.
   - All 96 satisfy length 13, regex structure, and AM/PM invariants.
   - Result: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T014/check.py`
   - Output: `FAIL: Smallest input mismatch: expected 'WRONG_VALUE', got '00: 00: 00 AM'`
   - Exit code: 1
