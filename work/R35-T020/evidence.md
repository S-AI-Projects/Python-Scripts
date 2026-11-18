# R35-T020 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T020 (Issue #20)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T020

## Target Item
- Module: `Password Manager/pwd_mgmr.py`
- Target class: `PasswordManager`
- Source fixture / data anchors: `self.pwd_dict = {}` (line 9)
- Preconditions established at: `Password Manager/pwd_mgmr.py`:
  - `Fernet` import (line 1)
  - `PasswordManager` (line 5)
  - `self.pwd_dict = {}` (line 9)
  - `add_password` (line 27)
  - `get_password` (line 36)

## Mutation Testing Design
- **Plausible One-Line Mistake**: A subtle casing alteration in `add_password` (e.g. `self.pwd_dict[site] = password.lower()` or truncation).
- **Protected Semantic Condition**: Password fidelity, case preservation, and entropy retention across encryption/decryption boundaries.
- **Minimal Differentiating Input**: Mixed-case password `"ComplexMixedCasePass!#99"`.
- **Differential Behavior**:
  - Original implementation stores and returns `"ComplexMixedCasePass!#99"` (PASS).
  - Mutated implementation returns `"complexmixedcasepass!#99"` (FAILS assertion `self.assertEqual(retrieved, raw_pwd)`).
  - Confirms the regression test detects plausible logic defects and prevents silent corruption.

## Verification Results
1. Source Anchor:
   - `self.pwd_dict = {}` verified on clean instance.
   - Result: PASS

2. Smallest valid input (`"a"`, `"b"`):
   - Input: site `"a"`, password `"b"`
   - Expected Output: `get_password("a") == "b"`
   - Actual Output: Matches expected
   - Result: PASS

3. Ordinary valid input (multi-site with Fernet encryption persistence):
   - Input: `"github.com"`, `"google.com"`
   - Expected Output: Correct decrypted passwords restored from encrypted file
   - Actual Output: Matches expected
   - Result: PASS

4. Mutation Detection:
   - Original passes assertion: PASS
   - Mutant fails assertion with semantic mismatch: PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T020/check.py`
   - Output: `FAIL: Smallest input mismatch: expected 'WRONG_VALUE', got 'b'`
   - Exit code: 1
