# R35-T032 Evidence

## Existing code and PR #62

- `PNG To JPG/main.py` found PNG files with `glob("*.png")`, opened each image,
  converted it to RGB, and saved a `.jpg` with quality 95.
- PR #62 is closed. It contains a proposed implementation and evidence, but those
  files are not present in the current worktree. This task does not copy the PR
  patch; its extra quality and file-existence validation rules are outside the
  requested boundary cases.

## Literal inputs and source preconditions

The precondition for both cases is established by `PNG To JPG/main.py` lines
10-13: every matched `.png` file is opened, converted to RGB, and saved as JPEG.
There is no source rule that rejects a 1x1 or 100x100 image.

| Boundary category | Literal input | Expected behavior | Source line |
|---|---|---|---|
| Smallest valid input | 1x1 RGBA PNG | Create 1x1 RGB JPEG named `tiny.jpg` | Lines 10-13 |
| Ordinary input | 100x100 RGB PNG | Create 100x100 RGB JPEG named `ordinary.jpg` | Lines 10-13 |

## Expected versus actual results

### Smallest valid input
- Input: 1x1 RGBA image, Pillow color `(255, 0, 0, 128)`, saved as `tiny.png`
- Expected return: `<temporary directory>/tiny.jpg`
- Expected file: exists
- Expected dimensions: `(1, 1)`
- Expected mode: `RGB`
- Expected format: `JPEG`
- Actual: PASS with the stated values

### Ordinary input
- Input: 100x100 RGB image, Pillow color `(10, 20, 30)`, saved as `ordinary.png`
- Expected return: `<temporary directory>/ordinary.jpg`
- Expected file: exists
- Expected dimensions: `(100, 100)`
- Expected mode: `RGB`
- Expected format: `JPEG`
- Actual: PASS with the stated values

## Tool versions

- Python: 3.15.2
- Pillow: 13.0.0

## Verification

- Baseline before implementation: 2 tests failed because
  `convert_png_to_jpg` did not exist.
- Final command: `python3 work/R35-T032/check.py`
- Number of tests executed: 2
