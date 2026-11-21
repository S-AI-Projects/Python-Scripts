"""
Focused repeatability and input-isolation regression tests for JSON to YAML (json_to_yaml.py).

Preconditions and source anchors:
- Anchor: import json, import yaml
- Anchor: 'Usage: json2yaml.py <sourcefile.json> [target_file.yaml]'
- Anchor: 'ERROR: ... not found'
- Anchor: 'ERROR: ... already exists'
"""

import copy
import io
import json
import os
import sys
import tempfile
import unittest

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import json_to_yaml


class TestJsonToYamlRepeatability(unittest.TestCase):
    """Test suite verifying repeatability, input isolation, and dependency control."""

    def setUp(self):
        self.smallest_input = {}
        self.smallest_expected_yaml = "{}\n"

        self.ordinary_input = {
            "name": "Python-Scripts",
            "version": 1,
            "active": True,
            "tags": ["python", "scripts"],
        }
        self.ordinary_expected_yaml = (
            "name: Python-Scripts\n"
            "version: 1\n"
            "active: true\n"
            "tags:\n"
            "- python\n"
            "- scripts\n"
        )

    def test_precondition_anchors(self):
        """Verify baseline source anchors in json_to_yaml.py."""
        source_path = os.path.join(MODULE_DIR, "json_to_yaml.py")
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("import json", content)
        self.assertIn("import yaml", content)
        self.assertIn("Usage: json2yaml.py <sourcefile.json> [target_file.yaml]", content)
        self.assertIn("already exists", content)

    def test_smallest_valid_input_fixture(self):
        """Test smallest valid JSON input ({}) conversion."""
        res = json_to_yaml.json_to_yaml(self.smallest_input)
        self.assertEqual(res, self.smallest_expected_yaml)

    def test_ordinary_valid_input_fixture(self):
        """Test ordinary valid JSON input conversion."""
        res = json_to_yaml.json_to_yaml(self.ordinary_input, sort_keys=False)
        self.assertEqual(res, self.ordinary_expected_yaml)

    def test_repeatability_and_input_isolation(self):
        """
        Run the ordinary fixture twice in fresh isolated state and once after another
        valid input; assert earlier runs cannot alter later results.
        """
        input_copy = copy.deepcopy(self.ordinary_input)

        # Run 1: Fresh isolated state
        run1 = json_to_yaml.json_to_yaml(self.ordinary_input, sort_keys=False)
        self.assertEqual(run1, self.ordinary_expected_yaml)

        # Run 2: Consecutive call in fresh isolated state
        run2 = json_to_yaml.json_to_yaml(self.ordinary_input, sort_keys=False)
        self.assertEqual(run1, run2)

        # Intervening run with distinct valid input
        intervening_input = {"author": "Tester", "score": [99.5, 100.0], "nested": {"key": "val"}}
        intervening_run = json_to_yaml.json_to_yaml(intervening_input, sort_keys=False)
        self.assertIn("author: Tester", intervening_run)

        # Run 3: Post-intervening run on the original input
        run3 = json_to_yaml.json_to_yaml(self.ordinary_input, sort_keys=False)
        self.assertEqual(run1, run3)

        # Assert input immutability
        self.assertEqual(self.ordinary_input, input_copy)

    def test_file_dependency_seam_and_repeatability(self):
        """
        Verify file-based conversion repeatability using temporary file isolation.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_file = os.path.join(tmp_dir, "input.json")
            yaml_file1 = os.path.join(tmp_dir, "output1.yaml")
            yaml_file2 = os.path.join(tmp_dir, "output2.yaml")

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(self.ordinary_input, f)

            # Execution 1
            out1 = json_to_yaml.convert_json_to_yaml(json_file, yaml_file1, sort_keys=False)
            with open(yaml_file1, "r", encoding="utf-8") as f:
                saved1 = f.read()

            # Execution 2
            out2 = json_to_yaml.convert_json_to_yaml(json_file, yaml_file2, sort_keys=False)
            with open(yaml_file2, "r", encoding="utf-8") as f:
                saved2 = f.read()

            self.assertEqual(out1, out2)
            self.assertEqual(saved1, saved2)
            self.assertEqual(saved1, self.ordinary_expected_yaml)

    def test_error_handling_dependency_seam(self):
        """Verify explicit error handling when source is missing or target already exists."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_source = os.path.join(tmp_dir, "nonexistent.json")
            with self.assertRaises(FileNotFoundError):
                json_to_yaml.convert_json_to_yaml(missing_source)

            # Target already exists
            src = os.path.join(tmp_dir, "src.json")
            tgt = os.path.join(tmp_dir, "tgt.yaml")
            with open(src, "w") as f:
                f.write("{}")
            with open(tgt, "w") as f:
                f.write("existing content")

            with self.assertRaises(FileExistsError):
                json_to_yaml.convert_json_to_yaml(src, tgt)


if __name__ == "__main__":
    unittest.main()
