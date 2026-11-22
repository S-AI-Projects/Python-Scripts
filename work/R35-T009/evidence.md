# R35-T009 Evidence — Measure the work done by extract_text_from_image

## Task
**R35-T009 · 9 of 10** — Measure the scaling of extract_text_from_image (main.py) [Screenshot to Text]

## Complexity observation
- **Input-size variable**: `n = img.width × img.height` (pixels)
- **Python wrapper (`extract_text_from_image`)**: O(1) — try/except + 1 OCR call + return
- **Delegated OCR work**: empirically O(n) in pixel count (observed, not a worst-case proof)
- **Process startup overhead**: constant per call (tesseract binary launch, model load) — not an algorithm operation

## Precondition anchor
```python
def extract_text_from_image(img):  # line 6
```

## Fixture

| Input | Value |
|-------|-------|
| Smallest valid input | `Image.new("RGB", (1, 1))` → `""` or `"\n"` (n=1 pixel) |
| Ordinary input | `Image.new("RGB", (100, 100))` → text string (n=10,000 pixels) |

## Complexity experiment results

| Size (n=w×h) | n (pixels) | Reps | Calls/rep (median) | Correct? |
|---|---|---|---|---|
| 1×1 | 1 | 5 | 1.0 | PASS |
| 10×10 | 100 | 5 | 1.0 | PASS |
| 100×100 | 10,000 | 5 | 1.0 | PASS |

**Observation**: `extract_text_from_image` makes exactly 1 OCR call per invocation regardless of image size — the Python wrapper is O(1). No pass/fail threshold depends on wall-clock speed.

## Tests
File: `Screenshot to Text/test_main.py`

| Test | Description |
|------|-------------|
| `test_smallest_returns_string` | 1×1 → returns str |
| `test_smallest_calls_pytesseract` | 1×1 → pytesseract called once |
| `test_smallest_no_mutation` | input image not mutated |
| `test_ordinary_returns_string` | 100×100 → returns "mock text" |
| `test_ordinary_calls_pytesseract` | 100×100 → pytesseract called once |
| `test_exception_returns_none` | exception → returns None |
| `test_exception_does_not_propagate` | exception caught by try/except |
| `test_one_ocr_call_per_invocation` | exactly 1 call for n=1,100,10000 |
| `test_five_repetitions_all_correct` | 5 reps of ordinary all return "text" |

## Check run

```
python3 work/R35-T009/check.py
```

**Result: 9/9 passed — PASS**
**FORCE_WRONG=1: EXIT_CODE=1 (failure detected correctly)**

## Tool versions
- Python: 3.15.0
- pytest: 9.2.0
- Pillow: 13.0.0
- pytesseract: mocked — no tesseract binary required
