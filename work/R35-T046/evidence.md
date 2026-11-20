# R35-T046 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T046 (Issue #46)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T046

## Target Item
- Module: `FileRenamer/File_Renamer.py`
- Target Function: `rename_files(directory, pattern, new_name)`
- Source Anchors:
  - `def rename_files(directory, pattern, new_name)` (Line 15 in original source)
  - `files = os.listdir(directory)` (Line 17 in original source)
  - `if re.match(pattern, file):` (Line 23 in original source)
- Precondition lines:
  - Line 17 establishes `directory` existence for `os.listdir`.
  - Line 23 establishes regex matching against filenames.
  - Lines 25-27 establish string concatenation for file extension and counter.

## Refactoring Explanation
- Extracted Responsibility: File extension parsing and target filename string synthesis extracted into `compute_renamed_filename(filename: str, new_name: str, counter: int) -> str`.
- Readability Improvement: Separates the pure formatting calculation (`compute_renamed_filename`) from the stateful filesystem traversal and renaming (`os.rename`).
- Interface Preservation: `rename_files(directory, pattern, new_name)` retains its exact public signature, parameter order, iteration semantics, and filesystem operations.
- Headless Safety: Guarded top-level `input(...)` prompts behind `if __name__ == '__main__':` to allow clean importing in test suites.

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification Results
1. Smallest Valid Input (1 file matching pattern):
   - Input: `directory="/photos"`, `pattern="IMG.*"`, `new_name="pic_"`, files=`["IMG_001.jpg"]`
   - Expected Rename: `/photos/IMG_001.jpg` -> `/photos/pic_0.jpg`
   - Actual Rename: `/photos/IMG_001.jpg` -> `/photos/pic_0.jpg`
   - Result: PASS

2. Ordinary Valid Input (multiple files, subset matching):
   - Input: `directory="/gallery"`, files=`["IMG_10.png", "notes.txt", "IMG_20.png"]`
   - Expected Renames: `IMG_10.png -> pic_0.png`, `IMG_20.png -> pic_1.png` (2 renames, `notes.txt` unchanged)
   - Actual Renames: 2 calls matching expected arguments
   - Result: PASS

3. Extracted Function Unit Verification:
   - Validated `compute_renamed_filename("photo.jpg", "vacation_", 0)` -> `"vacation_0.jpg"`
   - Result: PASS

4. Unit Test Suite Execution:
   - Command: `python3 -m unittest "FileRenamer/test_file_renamer.py"`
   - Ran 4 tests, 0 failures, 0 errors -> PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T046/check.py`
   - Output: `FAIL: Expected call('/photos/IMG_001.jpg', '/photos/WRONG_0.jpg'), got call('/photos/IMG_001.jpg', '/photos/pic_0.jpg')`
   - Exit code: 1
