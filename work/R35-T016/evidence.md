# R35-T016 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T016 (Issue #16)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T016

## Target Item
- Module: `Image to ASCII/main.py`
- Target function: `resize_image` and helper `calculate_new_dimensions`
- Preconditions established at: `Image to ASCII/main.py`:
  - `ASCII_CHARS` (line 4)
  - `calculate_new_dimensions` (line 7)
  - `resize_image` (line 24)

## Refactoring Summary
- **Extracted Responsibility**: Extracted aspect ratio dimension calculation out of `resize_image` into a dedicated helper function `calculate_new_dimensions(original_size, new_width=100) -> tuple[int, int]`.
- **Preserved Public Contract**: `resize_image(image, new_width=100)` retains identical signature, parameter names, and returns a PIL `Image` resized to proportional dimensions.
- **Improved Clarity & Testability**: Proportional dimension calculation is now purely testable independently of image pixel memory allocations and file operations.

## Verification Results
1. Smallest valid input (`1x1` image, `new_width=1`):
   - Input: 1x1 image, new_width=1
   - Expected Output: 1x1 resized image
   - Actual Output: 1x1
   - Result: PASS

2. Ordinary valid input (`200x100` image, `new_width=100`):
   - Input: 200x100 image, new_width=100
   - Expected Output: 100x50 resized image
   - Actual Output: 100x50
   - Result: PASS

3. Dimension Calculation Assertions:
   - Evaluated 5 diverse aspect ratios (1:1, 2:1, 1:3, 16:9).
   - Validated non-zero input checks (rejects width/height <= 0).
   - Result: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T016/check.py`
   - Output: `FAIL: Smallest input mismatch: expected (99, 99), got (1, 1)`
   - Exit code: 1
