# R35-T012 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T012 (Issue #12)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T012

## Target Item
- Module: `Remove Background/code.py`
- Target function: `remove_background`
- Preconditions established at: `Remove Background/code.py` lines 1-35 (module imports, input validation, 3-channel BGR type and range checks)

## Boundary Table

| Category | Input Condition | Expected Behavior | Source Line Reference |
| :--- | :--- | :--- | :--- |
| Valid Interior | Ordinary BGR image (100x100x3, threshold=250) | Converts to 100x100x4 BGRA image with alpha mask | `code.py:36-70` |
| Valid Boundary (Min Size) | Smallest valid BGR image (1x1x3 uint8) | Converts to 1x1x4 BGRA image, preserves BGR channels | `code.py:36-70` |
| Valid Boundary (Threshold Min) | threshold = 0 | Converts to valid BGRA image | `code.py:33-34` |
| Valid Boundary (Threshold Max) | threshold = 255 | Converts to valid BGRA image | `code.py:33-34` |
| Unsupported (None) | img = None | Raises `ValueError` | `code.py:27-28` |
| Unsupported (Dimensions) | 2D array or channel count != 3 | Raises `ValueError` | `code.py:31-32` |
| Unsupported (Zero Dimension) | Shape (0, 0, 3) | Raises `ValueError` | `code.py:33-34` |
| Unsupported (Threshold Out of Range) | threshold < 0 or > 255 | Raises `ValueError` | `code.py:35-36` |

## Verification Results
1. Smallest valid input (`1x1x3` BGR image):
   - Input: 1x1x3 uint8 array
   - Expected Output: 1x1x4 uint8 BGRA array
   - Actual Output: 1x1x4 uint8 BGRA array
   - Result: PASS

2. Ordinary valid input (`100x100x3` BGR image):
   - Input: 100x100x3 uint8 array
   - Expected Output: 100x100x4 uint8 BGRA array
   - Actual Output: 100x100x4 uint8 BGRA array
   - Result: PASS

3. Boundary Thresholds (0 and 255):
   - Both produce valid BGRA output without error.
   - Result: PASS

4. Unsupported Error Conditions:
   - None raises `ValueError`: PASS
   - 2D array raises `ValueError`: PASS
   - Zero dimension raises `ValueError`: PASS
   - Out-of-bounds threshold raises `ValueError`: PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T012/check.py`
   - Output: `FAIL: Deliberate mismatch triggered: expected (99, 99, 4), got (1, 1, 4)`
   - Exit code: 1
