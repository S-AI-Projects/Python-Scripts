# R35-T010 Evidence — Strengthen the tests of get_file_access_time

## Task
**R35-T010 · 10 of 10** — Strengthen the tests of get_file_access_time (recently_accessed_files.py) [Recently Accessed Files]

## Protected condition
```python
return os.path.getatime(file_path)   # line 4
```
**Plausible one-line mutant**: `os.path.getmtime(file_path)` instead of `os.path.getatime(file_path)`.

The test distinguishes the original from the mutant by mocking `getatime=1000.0` and `getmtime=2000.0` simultaneously and asserting the return equals `1000.0`. The original passes; the mutant returns `2000.0` and fails.

## Precondition anchors
```python
def get_file_access_time(file_path):  # line 4
recently_accessed_files = []          # line 9 (data anchor)
```

## Fixture

| Input | Expected output |
|-------|----------------|
| Smallest: `file_path=""` | `getatime("")` = `1000.0` (not `getmtime`=`2000.0`) |
| Ordinary: `file_path="/home/user/document.txt"` | `getatime(...)` = `5000.0` (not `getmtime`=`9999.0`) |

## Mutant analysis

| | Original | Mutant (`getmtime`) |
|---|---|---|
| `getatime` mock | 1000.0 | 1000.0 |
| `getmtime` mock | 2000.0 | 2000.0 |
| **Result** | **1000.0** ✅ | **2000.0** ❌ |
| Test outcome | PASS | FAIL |

## Tests
File: `Recently Accessed Files/test_recently_accessed_files.py`

| Test | Description |
|------|-------------|
| `test_smallest_returns_getatime_value` | "" → returns getatime 1000.0 |
| `test_smallest_returns_float` | returns float |
| `test_smallest_no_mutation` | input string unchanged |
| `test_ordinary_returns_getatime_value` | ordinary path → returns 5000.0 |
| `test_ordinary_passes_path_to_getatime` | getatime called with exact path |
| `test_returns_atime_not_mtime` | **mutation-resistant**: returns 1000.0, not getmtime 2000.0 |
| `test_returns_atime_not_ctime` | **mutation-resistant**: returns 1000.0, not getctime 3000.0 |
| `test_distinct_atime_mtime_ordinary` | ordinary: returns atime 5000.0 (not mtime 9999.0) |

## Check run

```
python3 work/R35-T010/check.py
```

**Result: 8/8 passed — PASS**
**FORCE_WRONG=1: EXIT_CODE=1 (mutant detected correctly)**

## Tool versions
- Python: 3.15.0
- pytest: 9.2.0
- os.path.getatime / getmtime / getctime: mocked — no real files required
