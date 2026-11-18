# R35-T017 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T017 (Issue #17)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T017

## Target Item
- Module: `Website Cloner/index.html` and `Website Cloner/runnable_example.py`
- Target workflow: End-to-end Website Cloner lifecycle
- Preconditions established at: `Website Cloner/index.html`:
  - `<!DOCTYPE html>` (line 1)
  - `<title>PROXY SERVER</title>` (line 8)
  - `<form class="login0-form validate-form" method="post" action="/" ...>` (line 18)
  - `<input class="input0" type="text" id="link" name="submitButton" ...>` (line 20)
  - `<button class="login0-form-btn" type="submit">CLONE NOW</button>` (line 27)

## Runnable Example Lifecycle & Intermediate States
The executable worked example (`Website Cloner/runnable_example.py`) exercises every intermediate step:
1. **Form Submission Payload**: Simulates client submitting form with URL encoded body (`submitButton=...`).
2. **Parameter Extraction**: `urllib.parse.parse_qs` extracts the raw URL.
3. **URL Normalization**: Prepends `'https://'` if protocol is omitted and strips trailing slashes.
4. **Folder Resolution**: Sanitizes URL into a safe filesystem subdirectory `./cloned_sites/<sanitized_name>`.
5. **Webpage Archiving**: Saves target page asset index into the destination folder.
6. **HTTP 301 Redirection**: Formulates HTTP redirection header `/cloned_sites/<sanitized_name>/index.html`.

## Verification Results
1. Smallest valid input (`example.com`):
   - Input: bare domain string `"example.com"`
   - Normalized URL: `"https://example.com"`
   - Output Redirection: `"/cloned_sites/example.com/index.html"`
   - Result: PASS

2. Ordinary valid input (`https://www.python.org`):
   - Input: full URL `"https://www.python.org"`
   - Normalized URL: `"https://www.python.org"`
   - Output Redirection: `"/cloned_sites/www.python.org/index.html"`
   - Result: PASS

3. Intermediate State Assertions:
   - All 6 stages asserted and verified during worked example execution.
   - Result: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T017/check.py`
   - Output: `FAIL: Smallest input mismatch: expected 'WRONG_URL', got 'https://example.com'`
   - Exit code: 1
