# R35-T038 Evidence

## Source behavior

The function is at `Star Pattern/starPattern.py` line 1.

- Line 9 establishes the empty/nested-loop
  branch. The outer loop is `range(1, n + 1)`.
- For `n = 0`, line 9 creates `range(1, 1)`, so the loop performs no rows.
- For `n = 1`, line 9 creates `range(1, 2)`, and the inner loop at line 10 prints
  one `* ` and line 12 prints a newline.
- For `n = 3`, the outer loop runs with i values 1, 2, and 3. The inner loop
  prints the corresponding number of `* ` values before line 12 prints newline.

The interactive input was originally at source line 8 and ran at import time.
It is now at lines 15-17 and protected by `if __name__ == "__main__":`.

## Literal inputs and expected results

| Input | Expected stdout | Expected return |
|---|---|---|
| `n = 1` | `* \n` | `None` |
| `n = 3` | `* \n* * \n* * * \n` | `None` |
| `n = 0` | `""` | `None` |

Preconditions:

- Smallest input `n = 1` reaches the outer loop at line 8 and inner loop once.
- Ordinary input `n = 3` reaches outer-loop values 1, 2, and 3.
- Empty input `n = 0` reaches `range(1, 1)` at line 8 and executes no loop body.

## Caller-state and follow-up call

The empty case uses an unchanged caller dictionary:
`{"unchanged": True}`.

- Before empty call: `{"unchanged": True}`
- After empty call: `{"unchanged": True}`
- Follow-up normal call: `starPattern(2)` prints `* \n* * \n`
- Caller state after follow-up: `{"unchanged": True}`

No exception was raised by `starPattern(0)`.

## Baseline

Before the import guard, the baseline test command failed while importing
`starPattern.py` because line 8 attempted interactive input and raised EOFError.

After the guard and docstring, all focused cases pass.

## Tool versions

- Python: 3.15.2
- Test framework: Python standard-library `unittest`

## Test command

```text
python3 work/R35-T038/check.py
```

- unittest test methods: 4
- Result: PASS
