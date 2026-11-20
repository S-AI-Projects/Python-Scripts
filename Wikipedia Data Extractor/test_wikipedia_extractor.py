import unittest
import sys
import os
import random
from unittest.mock import MagicMock, patch

# Mock wikipedia module if unavailable
if "wikipedia" not in sys.modules:
    mock_wiki = MagicMock()
    mock_wiki.summary = MagicMock(side_effect=lambda topic: f"Summary of {topic}")
    mock_wiki.set_lang = MagicMock()
    sys.modules["wikipedia"] = mock_wiki

# Ensure target directory is in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import wikipedia_extractor as we


class TestWikipediaExtractorInvariants(unittest.TestCase):
    """Property-based invariant unit tests for wikipedia_extractor."""

    def test_smallest_valid_input(self):
        """
        Smallest valid input: 1-character topic 'A' with default lang 'en'.
        Preconditions established by lines 3-4 in original source.
        """
        with patch.object(we.wikipedia, "summary", return_value="Summary of A") as mock_summary, \
             patch.object(we.wikipedia, "set_lang") as mock_set_lang:
            result = we.extract_summary("A")
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            self.assertEqual(result, "Summary of A")
            mock_set_lang.assert_called_with("en")
            mock_summary.assert_called_with("A")

    def test_ordinary_valid_input(self):
        """
        Ordinary valid input: topic 'Open Source' with lang 'jp'.
        Preconditions established by lines 6-9 in original source.
        """
        expected_text = "オープンソースの概要"
        with patch.object(we.wikipedia, "summary", return_value=expected_text) as mock_summary, \
             patch.object(we.wikipedia, "set_lang") as mock_set_lang:
            result = we.extract_summary("Open Source", lang="jp")
            self.assertIsInstance(result, str)
            self.assertEqual(result, expected_text)
            mock_set_lang.assert_called_with("jp")
            mock_summary.assert_called_with("Open Source")

    def test_property_invariants_100_bounded_cases(self):
        """
        Property test across 100 bounded valid inputs with deterministic seed (42).
        Verifies:
          1. Output type is always string
          2. Output length > 0
          3. Deterministic idempotency: extract_summary(t, l) == extract_summary(t, l)
          4. Non-mutation of input strings
        """
        rng = random.Random(42)
        languages = ["en", "jp", "es", "fr", "de"]

        for i in range(100):
            topic_len = rng.randint(1, 20)
            topic = "".join(rng.choices("abcdefghijklmnopqrstuvwxyz0123456789 _-", k=topic_len)).strip()
            if not topic:
                topic = f"Topic_{i}"
            lang = rng.choice(languages)

            synthetic_summary = f"Summary for topic [{topic}] in language [{lang}]"

            with patch.object(we.wikipedia, "summary", return_value=synthetic_summary), \
                 patch.object(we.wikipedia, "set_lang"):
                topic_copy = str(topic)
                lang_copy = str(lang)

                res1 = we.extract_summary(topic, lang=lang)
                res2 = we.extract_summary(topic, lang=lang)

                # Invariant 1: Output type
                self.assertIsInstance(res1, str, f"Case #{i}: output must be str")
                # Invariant 2: Non-empty length
                self.assertGreater(len(res1), 0, f"Case #{i}: output must be non-empty")
                # Invariant 3: Idempotency
                self.assertEqual(res1, res2, f"Case #{i}: idempotency violated")
                # Invariant 4: Input non-mutation
                self.assertEqual(topic, topic_copy, f"Case #{i}: topic mutated")
                self.assertEqual(lang, lang_copy, f"Case #{i}: lang mutated")

    def test_invalid_input_rejection(self):
        """
        Empty or non-string topics/languages violate preconditions and raise ValueError.
        """
        with self.assertRaises(ValueError):
            we.extract_summary("")
        with self.assertRaises(ValueError):
            we.extract_summary("Valid Topic", lang="")
        with self.assertRaises(ValueError):
            we.extract_summary(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
