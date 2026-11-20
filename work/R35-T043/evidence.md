# R35-T043 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T043 (Issue #43)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T043

## Target Item
- Module: `Image to GIF/imageTogif.py`
- Target Function: `make_gif(frame_folder, output_filepath="my_awesome.gif")`
- Anchor: `frame_one = frames[0]` (Line 5 in original source)
- Precondition lines:
  - Line 5 establishes `frame_one = frames[0]`, requiring `len(frames) >= 1`.
  - Lines 6-7 specify output parameters (`format="GIF"`, `append_images=frames`, `save_all=True`, `duration=100`, `loop=0`).

## Independent Reference Oracle
The independent oracle calculates expected GIF metadata directly from frame inputs without invoking `make_gif`:
```python
def independent_oracle(frame_list, output_name="my_awesome.gif"):
    if not frame_list:
        raise ValueError("No frames")
    return {
        "output_filepath": output_name,
        "format": "GIF",
        "total_frames": len(frame_list),
        "first_frame": frame_list[0],
        "duration": 100,
        "loop": 0,
        "save_all": True,
    }
```

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification Results
1. Anchor Check:
   - Evaluated `frame_one = frames[0]` anchor presence in source code.
   - Result: PASS

2. Smallest Valid Input (1 frame):
   - Input: Directory with 1 image (`img_0.JPG`)
   - Expected Output: `my_awesome.gif` saved with 1 frame, format="GIF", duration=100, loop=0
   - Actual Output: `my_awesome.gif` saved with matching kwargs
   - Result: PASS

3. Ordinary Valid Input (5 frames):
   - Input: Directory with 5 images (`img_0.JPG` .. `img_4.JPG`)
   - Expected Output: `ordinary.gif` saved with 5 frames appended
   - Actual Output: `ordinary.gif` saved with 5 frames appended
   - Result: PASS

4. Oracle Cross-Check across 25 Configurations:
   - Evaluated 25 distinct image frame counts (1 to 25 frames) against independent oracle.
   - 25 / 25 matched expected save attributes, format, duration, and frame counts (100% agreement).
   - Result: PASS

5. Unit Test Suite Execution:
   - Command: `python3 -m unittest "Image to GIF/test_image_to_gif.py"`
   - Ran 5 tests, 0 failures, 0 errors -> PASS

6. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T043/check.py`
   - Output: `FAIL: Expected WRONG_OUTPUT.gif, got my_awesome.gif`
   - Exit code: 1
