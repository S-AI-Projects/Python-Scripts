# R35-T034 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T034 (Issue #34)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T034

## Target Item
- Module: `Wallpaper Changer/wallpaperchanger.py`
- Target function: `add_margin(img, top, left, bottom, right, color)`
- Source line precondition: Line 57 (`add_margin` definition and calculation)

## Invariant Formalization
1. Dimension Preservation Invariant:
   `result.width == img.width + left + right`
   `result.height == img.height + top + bottom`
2. Mode Preservation Invariant:
   `result.mode == img.mode`
3. Sub-image Identity Invariant:
   `result.crop((left, top, left + img.width, top + img.height))` matches original image pixels identically.
4. Margin Color Invariant:
   Pixels strictly outside the pasted region retain the margin `color`.
5. Input Immutability Invariant:
   `img` size and underlying pixel buffer are untouched.

## Tool Versions
- Python: 3.15.2
- Pillow: 13.0.0
- OS: macOS (Darwin)

## Verification Results
1. Smallest Valid Input:
   - Input: 1x1 RGB image with `top=1, left=1, bottom=1, right=1`, `color=(0, 0, 0)`.
   - Expected Output Size: `(3, 3)`.
   - Center Pixel `(1, 1)`: matches original `(100, 150, 200)`.
   - Result: PASS

2. Ordinary Valid Input:
   - Input: 100x60 RGB image with `top=10, left=20, bottom=15, right=25`, `color=(255, 0, 0)`.
   - Expected Output Size: `(145, 85)`.
   - Crop at `(20, 10, 120, 70)` matches input pixels identically.
   - Result: PASS

3. Property-Based Testing across 100 Random Bounded Cases:
   - Seed: 42 (deterministic `random.Random(42)`)
   - 100 randomly generated image shapes and margin configurations tested.
   - All 4 invariants verified across all 100 cases without failure.
   - Result: PASS

4. Deliberate Invariant Break Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T034/check.py`
   - Output: `FAIL: Invariant broken: size (3, 3) != (99, 99)`
   - Exit code: 1
