# R35-T008 Evidence — Cover the failure behavior of getInformation

## Task
**R35-T008 · 8 of 10** — Cover the failure behavior of getInformation (univRanking.py) [University Rankings]

## Failure path documented
When `selectedCountry` is **not found** in any row of the rankings CSV, `number_of_universities` remains `0` and the line:

```python
averageScore = university_score / number_of_universities
```

raises `ZeroDivisionError`. This is the smallest input reaching the failure branch: a country name absent from the rankings CSV.

## Precondition anchors
```python
def getInformation(...)   # line 3
countries_lst = []        # line 15 — data anchor
continents_lst = []       # line 16 — data anchor
```

## Fixture

| Input | Value |
|-------|-------|
| Smallest valid (failure path) | `selectedCountry="Unknown"`, TopUni has 1 row for "USA" → ZeroDivisionError |
| Ordinary input (success path) | `selectedCountry="USA"`, same CSVs → completes without exception |

Independently calculated expected outputs (written before editing):
- `"Unknown"` → `ZeroDivisionError` (number_of_universities=0, division by zero)
- `""` → `ZeroDivisionError` (same reason)
- `"USA"` → `None` (side-effect only), `open("output.txt","w")` called
- After failure with `"Unknown"`, calling with `"USA"` still succeeds

## Also fixed
- Removed bare `__main__()` call at module level; added `if __name__ == "__main__"` guard so module is importable without blocking on `input()`.

## Tests
File: `University Rankings/test_univRanking.py`

| Test | Description |
|------|-------------|
| `test_unknown_country_raises_zero_division` | Failure path: "Unknown" → ZeroDivisionError |
| `test_empty_string_country_raises_zero_division` | Failure path: "" → ZeroDivisionError |
| `test_failure_does_not_mutate_caller_state` | Caller lists unchanged after failure |
| `test_ordinary_input_does_not_raise` | "USA" → no ZeroDivisionError |
| `test_ordinary_input_opens_output_file` | output.txt opened for writing |
| `test_success_after_failure` | "USA" succeeds immediately after "Unknown" fails |

## Check run

```
python3 work/R35-T008/check.py
```

**Result: 6/6 passed — PASS**
**FORCE_WRONG=1: EXIT_CODE=1 (failure detected correctly)**

## Tool versions
- Python: 3.15.0
- pytest: 9.2.0
- pandas: 3.1.1
- File I/O and pd.read_csv: mocked — no real CSV files needed
