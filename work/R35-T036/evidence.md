# R35-T036 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T036 (Issue #36)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T036

## Target Item
- Module: `InstaDownloader/insta_down.py`
- Target Function: `connection(url='http://www.google.com/', timeout=5)`
- Source line precondition: Lines 20-35 (HTTP GET probe, status handling, error branches)

## Refactoring Explanation
- Responsibility Extracted: Network reachability probe and exception classification extracted into `check_url_reachability(url, timeout)`.
- Benefit: Separates side-effecting display output (`print(...)`) from pure status evaluation (`(bool, str)`), making the connection logic testable, reusable, and free of mixed responsibilities.
- Preserved Interface: `connection(url='http://www.google.com/', timeout=5)` preserves its exact original signature, default arguments, printed messages, and boolean return values.

## Tool Versions
- Python: 3.15.2
- requests: 2.34.2
- OS: macOS (Darwin)

## Verification Results
1. Smallest Valid Input:
   - Input: `url="http://127.0.0.1", timeout=1`
   - Expected Output: `True`, with `"You're connected to internet\n"` printed.
   - Actual Output: `True`, printed `"You're connected to internet\n"`.
   - Result: PASS

2. Ordinary Valid Input:
   - Input: `url="http://www.google.com/", timeout=5`
   - Expected Output: `True`, with `"You're connected to internet\n"` printed.
   - Actual Output: `True`, printed `"You're connected to internet\n"`.
   - Result: PASS

3. Exception Path Verification:
   - HTTPError (status 503): returns `False` and formats status code.
   - ConnectionError: returns `False` with `"No internet connection available."`.
   - Result: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T036/check.py`
   - Output: `FAIL: Expected False, got True`
   - Exit code: 1
