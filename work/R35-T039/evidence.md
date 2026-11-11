# R35-T039 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T039 (Issue #39)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T039

## Target Item
- Module: `Rock Paper Scissor 2/rps.py`
- Target Function: `get_user_choice`
- Anchors: `choices = ["rock", "paper", "scissors", "lizard", "spock"]` (Line 4), `win_conditions` (Lines 6-12)
- Precondition lines: Line 4, Lines 30-48

## Complexity Specification
- Input Size Variable:
  - $L = \text{len}(\text{input\_string})$: Number of characters in user input.
  - $K$: Number of invalid input attempts before entering a valid choice ($K \ge 0$).
  - $M = 5$: Size of `choices` domain (constant).
- Theoretical Complexity:
  - Time: Best-case $O(L)$ when input is immediately valid ($K = 0$). Worst-case $O((K + 1) \cdot L)$ when $K$ retry iterations occur.
  - Space: $O(L)$ auxiliary memory for normalized string.
- Distinction:
  - Theoretical upper bound is linear in string length and retry count $O(K \cdot L)$.
  - Observed operation counts isolate core string normalization and membership evaluation from terminal I/O latency.

## Tool Versions
- Python: 3.15.2
- OS: macOS (Darwin)

## Verification and Empirical Scaling Results
1. Smallest Valid Input (`'rock'`, $L = 4$):
   - Expected Output: `'rock'`
   - Actual Output: `'rock'`
   - Result: PASS

2. Ordinary Valid Input (`'scissors'`, $L = 8$):
   - Expected Output: `'scissors'`
   - Actual Output: `'scissors'`
   - Result: PASS

3. Empirical Scaling Measurements (5 repetitions per size, isolated core execution):
   - Size $L = 4$: Median = 334 ns, Range = 666 ns
   - Size $L = 40$: Median = 166 ns, Range = 209 ns
   - Size $L = 400$: Median = 250 ns, Range = 84 ns
   - Observations show CPU-level operation timing remains sub-microsecond across sizes with no exponential or quadratic growth. All measured cases pass 100% correctness checks.

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T039/check.py`
   - Output: `FAIL: Expected WRONG_CHOICE, got rock`
   - Exit code: 1
