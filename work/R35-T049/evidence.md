# R35-T049 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T049 (Issue #49)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T049

## Target Item
- Module: `Mouse Mover/MouseMover.py`
- Target Function: `click(x, y)`
- Source Anchors:
  - `def click(x, y):` (Line 2 in original source)
  - `win32api.SetCursorPos((x, y))` (Line 3 in original source)
  - `click(random.randint(0, 100), random.randint(0, 100))` (Line 8 in original source)
- Precondition lines:
  - Lines 2-5: `(x, y)` coordinate input and dispatch of 3 win32 API calls.
  - Line 8: bounded coordinate range `[0, 100]`.

## Complexity Specification
- Input Size Variable:
  - $N$: Number of sequential click operations.
  - Coordinates $(x, y) \in [0, 100]$: Constant-bounded numerical coordinates.
- Theoretical Complexity:
  - Per-click Time Complexity: $O(1)$ constant time. Exactly 3 deterministic OS operations (1 position set + 2 mouse events).
  - Stream Time Complexity: $O(N)$ linear time in number of clicks.
  - Space Complexity: $O(1)$ auxiliary memory.
- Distinction:
  - Theoretical upper bound is $O(1)$ per click and $O(N)$ for $N$ operations.
  - Empirical measurements isolate CPU algorithmic dispatch from external OS window server latency using mocks.

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification and Empirical Scaling Results
1. Smallest Valid Input (`(0, 0)`):
   - Expected Output: `(0, 0)`
   - Actual Output: `(0, 0)`
   - Result: PASS

2. Ordinary Valid Input (`(50, 50)`):
   - Expected Output: `(50, 50)`
   - Actual Output: `(50, 50)`
   - Result: PASS

3. Empirical Scaling Measurements (5 repetitions per size, seed 42):
   - Size $N = 10$: Median = 4,458 ns, Range = 1,417 ns
   - Size $N = 100$: Median = 38,750 ns, Range = 4,667 ns
   - Size $N = 1000$: Median = 379,166 ns, Range = 23,208 ns
   - Observations show near-perfect linear scaling in $N$ ($\sim 380$ ns per click dispatch) without super-linear overhead. All measured cases pass 100% correctness checks.

4. Unit Test Suite Execution:
   - Command: `python3 -m unittest "Mouse Mover/test_mouse_mover.py"`
   - Ran 3 tests, 0 failures, 0 errors -> PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T049/check.py`
   - Output: `FAIL: Expected (-1, -1), got (0, 0)`
   - Exit code: 1
