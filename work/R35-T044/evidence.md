# R35-T044 Evidence

## Student Details
- Name: Suhani rai
- URN: e26b07f0577
- Task ID: R35-T044 (Issue #44)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0577/R35-T044

## Target Item
- Module: `Wikipedia Data Extractor/wikipedia_extractor.py`
- Target Item: `extract_summary(topic: str, lang: str = "en")`
- Source Anchors:
  - `wikipedia.summary(search)` (Line 4 in original source)
  - `wikipedia.set_lang(language)` (Line 7 in original source)
- Precondition lines:
  - Line 3: `search = input(...)` establishes string topic query.
  - Line 6: `language = "jp"` establishes language code selection.

## Invariant Formalization
1. Output Type Invariant:
   `isinstance(extract_summary(topic, lang), str)` is always True.
2. Non-Empty Result Invariant:
   `len(extract_summary(topic, lang)) > 0` for all valid queries.
3. Deterministic Idempotency Invariant:
   `extract_summary(topic, lang) == extract_summary(topic, lang)` under identical backend state.
4. Input Immutability Invariant:
   `topic` and `lang` parameters are never mutated or altered by extraction.

## Tool Versions
- Python: 3.14.7
- OS: macOS (Darwin arm64)

## Verification Results
1. Smallest Valid Input ('A', lang='en'):
   - Input: Topic `'A'`, language `'en'`
   - Expected Output: `"Summary of A"`
   - Actual Output: `"Summary of A"`
   - Result: PASS

2. Ordinary Valid Input ('Open Source', lang='jp'):
   - Input: Topic `'Open Source'`, language `'jp'`
   - Expected Output: `"オープンソースの概要"`
   - Actual Output: `"オープンソースの概要"`
   - Result: PASS

3. Property-Based Testing across 100 Random Bounded Cases:
   - Seed: 42 (deterministic `random.Random(42)`)
   - 100 generated combinations of topics (lengths 1-15) and languages (`en`, `jp`, `es`, `fr`, `de`).
   - Verified type invariance, non-empty text, idempotence, and input immutability across all 100 cases (100% agreement).
   - Result: PASS

4. Unit Test Suite Execution:
   - Command: `python3 -m unittest "Wikipedia Data Extractor/test_wikipedia_extractor.py"`
   - Ran 4 tests, 0 failures, 0 errors -> PASS

5. Deliberate Invariant Break Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T044/check.py`
   - Output: `FAIL: Expected BROKEN_INVARIANT, got Summary of A`
   - Exit code: 1
