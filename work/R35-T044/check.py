#!/usr/bin/env python3
import os
import sys
import unittest
import random
from unittest.mock import MagicMock, patch

# Mock wikipedia module if unavailable
if "wikipedia" not in sys.modules:
    mock_wiki = MagicMock()
    mock_wiki.summary = MagicMock(side_effect=lambda topic: f"Summary of {topic}")
    mock_wiki.set_lang = MagicMock()
    sys.modules["wikipedia"] = mock_wiki

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(ROOT_DIR, "Wikipedia Data Extractor")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import wikipedia_extractor as we


def run_checks():
    print("Running focused invariant checks for R35-T044: Wikipedia Data Extractor...")

    # Precondition and anchor check in source code
    source_file = os.path.join(TARGET_DIR, "wikipedia_extractor.py")
    with open(source_file, "r") as f:
        source_code = f.read()

    assert "wikipedia.summary" in source_code, (
        "Precondition anchor missing: wikipedia.summary"
    )
    assert "wikipedia.set_lang" in source_code, (
        "Precondition anchor missing: wikipedia.set_lang"
    )

    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Check 1: Smallest valid input (1-character topic)
    with patch.object(we.wikipedia, "summary", return_value="Summary of A") as mock_sum, \
         patch.object(we.wikipedia, "set_lang") as mock_sl:
        res_smallest = we.extract_summary("A")
        expected_smallest = "BROKEN_INVARIANT" if force_wrong else "Summary of A"
        print(f"[Smallest input 'A'] Result: {res_smallest}, Expected: {expected_smallest}")
        if res_smallest != expected_smallest:
            print(f"FAIL: Expected {expected_smallest}, got {res_smallest}")
            sys.exit(1)
        if not isinstance(res_smallest, str) or len(res_smallest) == 0:
            print("FAIL: String output invariant violated")
            sys.exit(1)

    # Check 2: Ordinary valid input ("Open Source", lang="jp")
    expected_ord = "オープンソースの概要"
    with patch.object(we.wikipedia, "summary", return_value=expected_ord):
        res_ord = we.extract_summary("Open Source", lang="jp")
        print(f"[Ordinary input 'Open Source' (jp)] Result: {res_ord}")
        if res_ord != expected_ord:
            print(f"FAIL: Expected {expected_ord}, got {res_ord}")
            sys.exit(1)

    # Check 3: Property tests across 100 bounded valid inputs with fixed seed 42
    rng = random.Random(42)
    languages = ["en", "jp", "es", "fr", "de"]
    for i in range(100):
        t_len = rng.randint(1, 15)
        topic = "".join(rng.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=t_len))
        lang = rng.choice(languages)
        expected_text = f"Summary content for {topic} [{lang}]"

        with patch.object(we.wikipedia, "summary", return_value=expected_text):
            r1 = we.extract_summary(topic, lang=lang)
            r2 = we.extract_summary(topic, lang=lang)

            assert isinstance(r1, str) and len(r1) > 0, f"Case #{i} type/length invariant violated"
            assert r1 == r2, f"Case #{i} idempotency invariant violated"
            assert r1 == expected_text, f"Case #{i} output text mismatch"

    print("[100 Bounded Property Invariant Cases]: PASS")

    # Run unittest suite in Wikipedia Data Extractor directory
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        print("FAIL: unittest suite failed")
        sys.exit(1)

    print(f"PASS: All invariant checks passed successfully (ran {res.testsRun} unittest cases).")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
