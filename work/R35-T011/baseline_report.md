# Baseline Analysis and Regression Specification

## 1. Module Analysis: `Face Reaction/app.py` (`load_custom_emojis`)

- **Function Under Test**: `load_custom_emojis(config_file='custom_emojis.json')` near line 8.
- **Public Inputs**:
  - `config_file` (str, optional): Path to the JSON configuration file containing emoji mappings. Defaults to `'custom_emojis.json'`.
- **Result**:
  - Returns a dictionary (`dict`) of emoji mappings loaded via `json.load(file)` if `os.path.exists(config_file)` evaluates to `True`.
  - Returns an empty dictionary (`{}`) if `os.path.exists(config_file)` evaluates to `False`.
- **Mutation Behavior**:
  - Pure query function: does not mutate caller arguments or global variables.
  - Specifically, it does not mutate `emotion_history` (precondition established at `Face Reaction/app.py:32`) or `org` (precondition established at `Face Reaction/app.py:85`).
- **External Dependencies**:
  - Filesystem I/O: `os.path.exists`, `open(config_file, 'r')`.
  - Serialization: `json.load`.
  - Module-level dependencies: `cv2`, `numpy`, `fer`.

---

## 2. Source Line Fixture & Preconditions

- **Anchor 1**: `Face Reaction/app.py:32` establishes `emotion_history = []`.
- **Anchor 2**: `Face Reaction/app.py:85` establishes `org = (40, 210)`.

---

## 3. Independently Calculated Expected Outputs

Before running the source code, independent expected outputs were calculated for the fixtures:

1. **Smallest Valid Input**:
   - Literal input content: `"{}"` (valid empty JSON object).
   - Expected return: `{}`.
   - Expected mutation: None. `emotion_history` remains `[]`, `org` remains `(40, 210)`.

2. **Ordinary Input**:
   - Literal input content: `{"happy": "emojis/happy.png", "sad": "emojis/sad.png", "angry": "emojis/angry.png"}`.
   - Expected return: `{"happy": "emojis/happy.png", "sad": "emojis/sad.png", "angry": "emojis/angry.png"}`.
   - Expected mutation: None. `emotion_history` remains `[]`, `org` remains `(40, 210)`.

3. **Repeated-Value Domain Boundary Input**:
   - Literal input content: `{"happy": "emojis/common_smile.png", "surprise": "emojis/common_smile.png", "excited": "emojis/common_smile.png"}` (multiple keys mapping to repeated emoji file).
   - Expected return: `{"happy": "emojis/common_smile.png", "surprise": "emojis/common_smile.png", "excited": "emojis/common_smile.png"}`.
   - Expected mutation: None. `emotion_history` remains `[]`, `org` remains `(40, 210)`.

4. **Missing File Boundary Input**:
   - Literal input: `'nonexistent_custom_emojis.json'`.
   - Expected return: `{}`.
   - Expected mutation: None. `emotion_history` remains `[]`, `org` remains `(40, 210)`.

---

## 4. Baseline Execution & Defect Explanation

When running tests against the original, unedited `Face Reaction/app.py`:
- **Command**: `python3 "Face Reaction/tests/test_app.py"`
- **Result**: FAILED with `ValueError: not enough values to unpack (expected 2, got 0)` during module import (`import app`, line 35 `ret, frame = scr.read()`).
- **Defect Analysis**:
  In the original implementation, executable code (webcam initialization `scr = cv2.VideoCapture(0)`, FER detector setup `detector = FER(mtcnn=True)`, and the main processing loop `while True:`) was placed directly at module top level (lines 20–100) without an `if __name__ == '__main__':` guard.
  Consequently, importing `app` as a module triggers hardware acquisition and camera reading at import time, preventing modular reuse and unit testing of `load_custom_emojis`.
- **Remediation**:
  Wrap the runtime camera capture and detection loop in a `main()` function protected by `if __name__ == '__main__':`, while retaining module anchors `emotion_history = []` and `org = (40, 210)`. This fixes the defect, enables clean imports with external I/O mocked, and completely preserves existing runtime behavior when executed as a script.
