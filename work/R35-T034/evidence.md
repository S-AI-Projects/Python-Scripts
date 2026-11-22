# R35-T034 Evidence

## Previous PR #64

PR #64 was closed. Its proposed patch added tests and broad import/main guard
changes, but it was not present locally. The initial `wallpaperchanger.py` had
top-level wallpaper operations and directly imported optional dependencies.
PR #64 also did not require retaining as-is; this task applies narrower fixes.

## Existing and corrected behavior

The existing `add_margin()` implementation already had the required dimensions,
mode, paste position, and original-input behavior:

- `new_width = width + right + left`
- `new_height = height + top + bottom`
- `Image.new(img.mode, ...)`
- `result.paste(img, (left, top))`

Source preconditions:

- `add_margin()` begins at line 38.
- Original dimensions are read at line 49.
- New dimensions are calculated at lines 50-51.
- Output mode and content are established at lines 52-53.

The implementation needed testability fixes:

- Added fallback handling for optional imports.
- Added a `main()` guard so wallpaper operations do not run during test import.

`add_margin()` itself was not changed.

## Boundary and ordinary inputs

| Case | Original | Margins top/left/bottom/right | Margin color | Expected result |
|---|---|---|---|---|
| Smallest | 1x1 RGB `(100,150,200)` | 1/1/1/1 | `(0,0,0)` | `(3,3)` RGB |
| Ordinary | 100x60 RGB `(50,60,70)` | 10/20/15/25 | `(255,0,0)` | `(145,85)` RGB |

Smallest expected:

- Size: `(3, 3)`
- Mode: `RGB`
- Pixel `(1,1)`: `(100,150,200)`
- Every other pixel: `(0,0,0)`
- Original remains `(1,1)` with the original pixel unchanged

Ordinary expected:

- Size: `(145,85)`
- Mode: `RGB`
- Crop `(20,10,120,70)` equals the original image exactly
- Every pixel outside that crop equals `(255,0,0)`
- Original remains `(100,60)` and unchanged

## Generated cases

- Generator: `random.Random(42)`
- Count: 100
- Width and height: 1 through 50 pixels
- Margins: 0 through 20 pixels
- Modes: `RGB` or `L`
- Every case independently checks size, mode, placed content, original
  immutability, and margin pixels.

## Deliberate failure

A temporary copy of `wallpaperchanger.py` replaces
`new_width = width + right + left` with `new_width = width + left`.
The 1x1 case then reports `(2,3)` instead of `(3,3)`, and the runner detects
the mismatch.

## Tool versions

- Python: 3.15.2
- Pillow: 13.0.0

## Final command

- Command: `python3 work/R35-T034/check.py`
- unittest methods: 3
- generated bounded configurations: 100
- Result: PASS
