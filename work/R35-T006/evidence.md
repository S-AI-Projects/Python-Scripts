# R35-T006 Evidence — Simplify one responsibility in No Screensaver

## Task
**R35-T006 · 6 of 10** — Simplify one responsibility in No Screensaver (`noscreensaver.py`) [No Screensaver]

## What was simplified
The original script embedded magic numbers `50` and `400` (the click co-ordinates) **and** the constant `40` (sleep interval) directly inside an infinite loop body. These literals had no names and no way to override them without editing the source.

The extracted responsibility is **parameterised click position and sleep interval**: a function `keep_awake(interval_seconds, click_x, click_y)` now names each co-ordinate explicitly. The loop body shrinks to a single call, making the purpose of each value clear at a glance.

The algorithm, return type, side-effect ordering (sleep → click), and public behaviour are all preserved.

## Precondition anchor
```python
import pyautogui  # line 1 — precondition: pyautogui must be importable
```

## Fixture

| Input | Value |
|-------|-------|
| Smallest valid input | `interval_seconds=1, click_x=0, click_y=0` |
| Ordinary input | `interval_seconds=40, click_x=50, click_y=400` |

Independently calculated expected outputs (written before editing):
- `pyautogui.sleep` called once with `interval_seconds`
- `pyautogui.click` called once with `(click_x, click_y)`
- Return value: `None`
- Order: sleep always before click

## Tests
File: `No Screensaver/test_noscreensaver.py`

| Test | Description |
|------|-------------|
| `test_sleep_called_with_smallest_interval` | sleep(1) for smallest input |
| `test_click_called_with_smallest_coords` | click(0,0) for smallest input |
| `test_return_value_is_none_smallest` | None returned for smallest input |
| `test_sleep_before_click_smallest` | order preserved, smallest |
| `test_sleep_called_with_ordinary_interval` | sleep(40) for ordinary input |
| `test_click_called_with_ordinary_coords` | click(50,400) for ordinary input |
| `test_return_value_is_none_ordinary` | None returned for ordinary input |
| `test_sleep_before_click_ordinary` | order preserved, ordinary |
| `test_defaults_match_original_hardcoded_values` | defaults replicate original behaviour |
| `test_isolated_calls_do_not_share_state` | consecutive calls are independent |

## Check run

```
python3 work/R35-T006/check.py
```

**Result: 10/10 passed — PASS**
**FORCE_WRONG=1: EXIT_CODE=1 (failure detected correctly)**

## Diff summary (before → after)

**Before:**
```python
import pyautogui
while 1>0:
    pyautogui.sleep(40)
    pyautogui.click(50, 400)
```

**After:**
```python
def keep_awake(interval_seconds=40, click_x=50, click_y=400) -> None:
    pyautogui.sleep(interval_seconds)
    pyautogui.click(click_x, click_y)

def _run_loop(...):
    while True:
        keep_awake(...)

if __name__ == "__main__":
    _run_loop()
```

## Tool versions
- Python: 3.15.0
- pytest: 9.2.0
- pyautogui: (mocked — no display needed)
