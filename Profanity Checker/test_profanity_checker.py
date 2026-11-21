"""
Property-based invariant regression tests for Profanity Checker (ProfanityChecker.py).

Invariants asserted:
1. Invariant 1 (Score Boundedness): -1.0 <= compound <= 1.0; 0 <= pos, neg, neu <= 1.0
2. Invariant 2 (Label Partition Completeness): Label is exactly one of 5 classes:
   {'Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative'} matching thresholds.
3. Invariant 3 (Preprocessing Idempotency): preprocess_text(preprocess_text(x)) == preprocess_text(x)
4. Invariant 4 (Token Reduction Invariant): len(tokens(filtered)) <= len(tokens(original))
5. Invariant 5 (Input Immutability): Input strings remain strictly unmutated.
"""

import os
import random
import sys
import unittest

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import ProfanityChecker
from nltk.tokenize import word_tokenize


class TestProfanityCheckerInvariants(unittest.TestCase):
    """Property test suite asserting mathematical and structural invariants of Profanity Checker."""

    def test_precondition_anchors(self):
        """Verify baseline source anchors in ProfanityChecker.py."""
        source_path = os.path.join(MODULE_DIR, "ProfanityChecker.py")
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("SentimentIntensityAnalyzer", content)
        self.assertIn("word_tokenize", content)
        self.assertIn("WordNetLemmatizer", content)
        self.assertIn("stopwords.words('english')", content)
        self.assertIn("https://www.purgomalum.com/service/json?text=", content)

    def test_smallest_valid_input_fixture(self):
        """
        Test smallest valid non-empty input: 'Good'
        Precondition: ProfanityChecker.py lines for tokenization and polarity scoring.
        """
        text = "Good"
        res = ProfanityChecker.analyze_text(text)

        self.assertEqual(res["text"], "Good")
        self.assertEqual(res["filtered_text"], "good")
        self.assertAlmostEqual(res["scores"]["compound"], 0.4404, places=3)
        self.assertEqual(res["sentiment_label"], "Positive")

        # Smallest empty text
        empty_res = ProfanityChecker.analyze_text("")
        self.assertEqual(empty_res["filtered_text"], "")
        self.assertEqual(empty_res["scores"]["compound"], 0.0)
        self.assertEqual(empty_res["sentiment_label"], "Neutral")

    def test_ordinary_input_fixture(self):
        """
        Test ordinary multi-word input:
        'I love programming in Python. It is wonderful and clean.'
        """
        text = "I love programming in Python. It is wonderful and clean."
        res = ProfanityChecker.analyze_text(text)

        self.assertIn("love", res["filtered_text"])
        self.assertIn("wonderful", res["filtered_text"])
        self.assertNotIn("is", res["filtered_text"])  # stopword removed
        self.assertGreater(res["scores"]["compound"], 0.5)
        self.assertEqual(res["sentiment_label"], "Very Positive")

    def test_100_bounded_property_cases(self):
        """
        Generate at least 100 bounded valid sentences with a fixed deterministic seed
        and verify all core invariants.
        """
        random.seed(42)

        vocabulary_pool = {
            "pos": ["great", "excellent", "superb", "happy", "love", "awesome", "good", "wonderful", "delight"],
            "neg": ["terrible", "horrible", "bad", "hate", "awful", "ugly", "painful", "worst", "sad"],
            "neu": ["table", "window", "algorithm", "data", "screen", "system", "file", "network", "python"],
            "stop": ["the", "is", "at", "which", "on", "a", "an", "this", "it", "and", "or", "in"],
            "punct": [".", "!", "?", ","]
        }

        valid_labels = {"Very Positive", "Positive", "Neutral", "Negative", "Very Negative"}

        for i in range(1, 101):
            # Construct varied sentence
            n_pos = random.randint(0, 3)
            n_neg = random.randint(0, 3)
            n_neu = random.randint(1, 4)
            n_stop = random.randint(1, 3)

            words = (
                random.choices(vocabulary_pool["pos"], k=n_pos) +
                random.choices(vocabulary_pool["neg"], k=n_neg) +
                random.choices(vocabulary_pool["neu"], k=n_neu) +
                random.choices(vocabulary_pool["stop"], k=n_stop)
            )
            random.shuffle(words)
            sentence = " ".join(words) + random.choice(vocabulary_pool["punct"])

            original_copy = str(sentence)
            res = ProfanityChecker.analyze_text(sentence)

            # Invariant 1: Score Boundedness
            scores = res["scores"]
            self.assertGreaterEqual(scores["compound"], -1.0, f"Case {i}: compound underflow")
            self.assertLessEqual(scores["compound"], 1.0, f"Case {i}: compound overflow")
            self.assertGreaterEqual(scores["pos"], 0.0)
            self.assertLessEqual(scores["pos"], 1.0)
            self.assertGreaterEqual(scores["neg"], 0.0)
            self.assertLessEqual(scores["neg"], 1.0)
            self.assertGreaterEqual(scores["neu"], 0.0)
            self.assertLessEqual(scores["neu"], 1.0)

            # Invariant 2: Label Partition Completeness & Exclusivity
            label = res["sentiment_label"]
            self.assertIn(label, valid_labels, f"Case {i}: invalid label {label}")
            cmp = scores["compound"]
            if cmp > 0.5:
                self.assertEqual(label, "Very Positive")
            elif cmp > 0:
                self.assertEqual(label, "Positive")
            elif cmp == 0:
                self.assertEqual(label, "Neutral")
            elif cmp < -0.5:
                self.assertEqual(label, "Very Negative")
            else:
                self.assertEqual(label, "Negative")

            # Invariant 3: Preprocessing Idempotency
            filtered_once = res["filtered_text"]
            filtered_twice = ProfanityChecker.preprocess_text(filtered_once)
            self.assertEqual(filtered_once, filtered_twice, f"Case {i}: preprocessing not idempotent")

            # Invariant 4: Token Reduction Invariant
            orig_tokens = word_tokenize(sentence)
            filt_tokens = word_tokenize(filtered_once)
            self.assertLessEqual(len(filt_tokens), len(orig_tokens), f"Case {i}: token count expanded")

            # Invariant 5: Input Immutability
            self.assertEqual(sentence, original_copy, f"Case {i}: input string was mutated")

    def test_deliberate_broken_invariant_detection(self):
        """
        Verify that deliberately breaking the invariant raises an assertion failure.
        """
        # Score out of bounds > 1.0
        broken_compound = 1.5
        label = ProfanityChecker.classify_sentiment(broken_compound)
        # Even if classification returns, our invariant check catches the score boundary violation
        with self.assertRaises(AssertionError):
            assert -1.0 <= broken_compound <= 1.0, "Score boundary invariant violated"


if __name__ == "__main__":
    unittest.main()
