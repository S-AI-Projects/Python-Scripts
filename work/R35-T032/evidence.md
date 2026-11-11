# R35-T032 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T032 (Issue #32)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T032

## Target Item
- Module: `PNG To JPG/main.py`
- Target item: `PNG To JPG` conversion logic (`convert_png_to_jpg`)
- Preconditions established at: `PNG To JPG/main.py` lines 7-23 (contract docstring, file existence checks, valid quality parameter)

## Boundary Table

| Category | Input Condition | Expected Behavior | Source Line Reference |
| :--- | :--- | :--- | :--- |
| Valid Interior | Ordinary PNG (100x100 RGB, quality=95) | Converts to 100x100 JPEG, returns target path | lines 25-28 |
| Valid Boundary (Min Size) | Smallest valid PNG (1x1 RGBA) | Converts to 1x1 RGB JPEG with alpha flattened | lines 25-28 |
| Valid Boundary (Quality Min) | Quality = 1 | Saves valid lowest-quality JPEG | lines 23-24 |
| Valid Boundary (Quality Max) | Quality = 100 | Saves valid highest-quality JPEG | lines 23-24 |
| Unsupported (File) | Non-existent path | Raises `FileNotFoundError` | line 22 |
| Unsupported (Quality Out of Range) | Quality = 0 or 101 | Raises `ValueError` | lines 23-24 |

## Tool Versions
- Python: 3.15.2
- Pillow: 13.0.0
- OS: macOS (Darwin)

## Verification Results
1. Smallest valid input (`1x1` PNG):
   - Input: 1x1 RGBA PNG
   - Expected Output: 1x1 RGB JPEG file created
   - Actual Output: 1x1 RGB JPEG created
   - Result: PASS

2. Ordinary valid input (`100x100` PNG):
   - Input: 100x100 RGB PNG
   - Expected Output: 100x100 RGB JPEG file created
   - Actual Output: 100x100 RGB JPEG created
   - Result: PASS

3. Boundary Quality (1 and 100):
   - Both produce valid JPEG output without error.
   - Result: PASS

4. Unsupported Error Conditions:
   - Non-existent file raises `FileNotFoundError`: PASS
   - Quality 0 / 101 raises `ValueError`: PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T032/check.py`
   - Output: `FAIL: Expected size (99, 99), got (1, 1)`
   - Exit code: 1
