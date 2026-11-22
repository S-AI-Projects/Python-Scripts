# R35-T039 Evidence

## Function behavior and input size

`get_user_choice()` reads one string from `input()`, converts it with
`.lower()`, and checks whether it is in the global `choices` list.
If the value is not in the list, the `while` loop reads and checks another
string until it is valid. It returns the accepted lowercase string.

- Choices and fixed domain size: `Rock Paper Scissor 2/rps.py` line 3
- First input and `.lower()`: line 10
- Retry condition and repeated input: lines 11-12
- Return value: line 13

The input-size variable is the number of characters in one entered string.
`.lower()` processes those characters. List membership may compare up to five
choices; comparing strings can inspect characters too. Because the list stays
fixed at five entries, one attempt is O(n) in the string length. If the user
enters multiple invalid strings, the total work is proportional to the sum of
the lengths of all attempts.

## Test inputs and expected versus actual outputs

Source line 3 defines which inputs are valid; source line 10 normalizes the
input, and lines 11-13 implement retry and return.

| Case | Literal input | Expected return | Actual |
|---|---|---|---|
| Smallest valid | `"rock"` | `"rock"` | `"rock"` |
| Ordinary valid | `"scissors"` | `"scissors"` | `"scissors"` |
| Retry | `"invalid"`, then `"paper"` | `"paper"` after 2 input calls | `"paper"` after 2 input calls |

All tests use mocked `input()` and no manual interaction.

## Operation-count experiment

Timing was not used because the valid choices have a tiny fixed domain and
short strings, making wall-clock results dominated by measurement noise.
Instead, an operation-count model counts one unit for each input character
lowercased plus one unit for each choice-list entry checked. Comparisons are
bounded by the five choices in the fixed list.

The experiment uses `random.Random(42)`, fresh mixed-case strings for every
run, and five repetitions for each increasing valid string length. The target
word is reconstructed from newly joined characters on each repetition.

| Input length | Valid word | Five modeled counts | Median | Range |
|---:|---|---|---:|---:|
| 4 | rock | 5, 5, 5, 5, 5 | 5 | 5..5 |
| 5 | spock | 10, 10, 10, 10, 10 | 10 | 10..10 |
| 8 | scissors | 11, 11, 11, 11, 11 | 11 | 11..11 |

The count equals input length plus the number of list entries checked:
rock is first (1), spock is fifth (5), and scissors is third (3).
These are operation-model results, not elapsed-time measurements.

## Tool versions and test results

- Python: 3.15.2
- Test framework: standard-library `unittest`
- Timing packages: none
- Tests: 3 passed
- Complexity experiment: 15 calls total (5 per input length), passed

Exact command:

```text
python3 work/R35-T039/check.py
```

Result: `PASS`
