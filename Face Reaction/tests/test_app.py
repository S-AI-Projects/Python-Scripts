import os
import sys
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure Face Reaction directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Mock external hardware/model dependencies (cv2, fer, numpy) if not present
for mod_name in ("cv2", "fer"):
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()
if "numpy" not in sys.modules:
    try:
        import numpy
    except ImportError:
        sys.modules["numpy"] = MagicMock()

# Import the module under test
import app
from app import load_custom_emojis


class TestLoadCustomEmojisReturnValues(unittest.TestCase):
    """
    Focused regression tests for load_custom_emojis return values.
    Source line: Face Reaction/app.py:8 establishes load_custom_emojis.
    Preconditions:
      - Face Reaction/app.py:32 establishes emotion_history = []
      - Face Reaction/app.py:85 establishes org = (40, 210)
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_smallest_valid_input(self):
        """
        Smallest valid input test:
        Literal input: JSON file containing empty object '{}'.
        Independently calculated expected output: {}.
        Preconditions:
          - Face Reaction/app.py:32 establishes emotion_history = []
          - Face Reaction/app.py:85 establishes org = (40, 210)
        """
        config_path = os.path.join(self.temp_dir.name, "smallest_config.json")
        literal_input_content = "{}"
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(literal_input_content)

        expected_output = {}
        actual_output = load_custom_emojis(config_path)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Expected {expected_output!r}, but got {actual_output!r} for input {literal_input_content!r}",
        )
        self.assertIsInstance(actual_output, dict)

    def test_ordinary_input(self):
        """
        Ordinary input test:
        Literal input: JSON file mapping typical emotions to image paths.
        Independently calculated expected output: matching dictionary of emotion -> path.
        Preconditions:
          - Face Reaction/app.py:32 establishes emotion_history = []
          - Face Reaction/app.py:85 establishes org = (40, 210)
        """
        config_path = os.path.join(self.temp_dir.name, "ordinary_config.json")
        literal_input_dict = {
            "happy": "emojis/happy.png",
            "sad": "emojis/sad.png",
            "angry": "emojis/angry.png",
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(literal_input_dict, f)

        expected_output = {
            "happy": "emojis/happy.png",
            "sad": "emojis/sad.png",
            "angry": "emojis/angry.png",
        }
        actual_output = load_custom_emojis(config_path)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Expected {expected_output!r}, but got {actual_output!r} for input {literal_input_dict!r}",
        )
        self.assertEqual(len(actual_output), 3)

    def test_repeated_value_boundary_input(self):
        """
        Repeated-value domain boundary test:
        Literal input: JSON file with multiple emotion keys mapping to the identical emoji image path.
        Independently calculated expected output: dictionary preserving multiple keys mapping to repeated value.
        Preconditions:
          - Face Reaction/app.py:32 establishes emotion_history = []
          - Face Reaction/app.py:85 establishes org = (40, 210)
        """
        config_path = os.path.join(self.temp_dir.name, "repeated_value_config.json")
        literal_input_dict = {
            "happy": "emojis/common_smile.png",
            "surprise": "emojis/common_smile.png",
            "excited": "emojis/common_smile.png",
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(literal_input_dict, f)

        expected_output = {
            "happy": "emojis/common_smile.png",
            "surprise": "emojis/common_smile.png",
            "excited": "emojis/common_smile.png",
        }
        actual_output = load_custom_emojis(config_path)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Expected {expected_output!r}, but got {actual_output!r} for input {literal_input_dict!r}",
        )
        # Verify repeated values exist
        values = list(actual_output.values())
        self.assertEqual(len(values), 3)
        self.assertEqual(len(set(values)), 1)

    def test_missing_file_boundary_input(self):
        """
        Missing file boundary test:
        Literal input: Path to non-existent file.
        Independently calculated expected output: {}.
        Preconditions:
          - Face Reaction/app.py:32 establishes emotion_history = []
          - Face Reaction/app.py:85 establishes org = (40, 210)
        """
        non_existent_path = os.path.join(self.temp_dir.name, "does_not_exist.json")
        expected_output = {}
        actual_output = load_custom_emojis(non_existent_path)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Expected {expected_output!r}, but got {actual_output!r} for non-existent file",
        )


class TestLoadCustomEmojisObservableMutation(unittest.TestCase):
    """
    Focused regression tests verifying that load_custom_emojis does NOT perform
    any observable mutations on global state or caller data.
    Tested separately from return values.
    Source line: Face Reaction/app.py:8 establishes load_custom_emojis.
    Preconditions:
      - Face Reaction/app.py:32 establishes emotion_history = []
      - Face Reaction/app.py:85 establishes org = (40, 210)
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        # Verify preconditions anchored in source lines before each test
        # Precondition anchor 1: Face Reaction/app.py:32 -> emotion_history = []
        # Precondition anchor 2: Face Reaction/app.py:85 -> org = (40, 210)
        self.precondition_emotion_history = []
        self.precondition_org = (40, 210)

        # Set or reset module anchors if present
        if hasattr(app, "emotion_history"):
            app.emotion_history = []
        if hasattr(app, "org"):
            app.org = (40, 210)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_no_mutation_with_smallest_valid_input(self):
        """
        Verify no observable mutation when invoking with smallest valid input.
        Preconditions:
          - Face Reaction/app.py:32 establishes emotion_history = []
          - Face Reaction/app.py:85 establishes org = (40, 210)
        """
        config_path = os.path.join(self.temp_dir.name, "smallest_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("{}")

        # Snapshot state before call
        history_before = list(getattr(app, "emotion_history", self.precondition_emotion_history))
        org_before = getattr(app, "org", self.precondition_org)

        # Execute
        load_custom_emojis(config_path)

        # Assert no observable mutation on state
        history_after = list(getattr(app, "emotion_history", self.precondition_emotion_history))
        org_after = getattr(app, "org", self.precondition_org)

        self.assertEqual(
            history_after,
            history_before,
            f"Mutation detected: emotion_history changed from {history_before!r} to {history_after!r}",
        )
        self.assertEqual(
            history_after,
            [],
            "Precondition Face Reaction/app.py:32 violated: emotion_history should remain []",
        )
        self.assertEqual(
            org_after,
            org_before,
            f"Mutation detected: org changed from {org_before!r} to {org_after!r}",
        )
        self.assertEqual(
            org_after,
            (40, 210),
            "Precondition Face Reaction/app.py:85 violated: org should remain (40, 210)",
        )

    def test_no_mutation_with_ordinary_input(self):
        """
        Verify no observable mutation when invoking with ordinary input.
        Preconditions:
          - Face Reaction/app.py:32 establishes emotion_history = []
          - Face Reaction/app.py:85 establishes org = (40, 210)
        """
        config_path = os.path.join(self.temp_dir.name, "ordinary_config.json")
        literal_data = {"happy": "emojis/happy.png", "sad": "emojis/sad.png"}
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(literal_data, f)

        # Snapshot state before call
        history_before = list(getattr(app, "emotion_history", self.precondition_emotion_history))
        org_before = getattr(app, "org", self.precondition_org)

        # Execute
        load_custom_emojis(config_path)

        # Assert no observable mutation
        history_after = list(getattr(app, "emotion_history", self.precondition_emotion_history))
        org_after = getattr(app, "org", self.precondition_org)

        self.assertEqual(
            history_after,
            history_before,
            f"Mutation detected: emotion_history changed from {history_before!r} to {history_after!r}",
        )
        self.assertEqual(
            history_after,
            [],
            "Precondition Face Reaction/app.py:32 violated: emotion_history should remain []",
        )
        self.assertEqual(
            org_after,
            org_before,
            f"Mutation detected: org changed from {org_before!r} to {org_after!r}",
        )
        self.assertEqual(
            org_after,
            (40, 210),
            "Precondition Face Reaction/app.py:85 violated: org should remain (40, 210)",
        )


if __name__ == "__main__":
    unittest.main()
