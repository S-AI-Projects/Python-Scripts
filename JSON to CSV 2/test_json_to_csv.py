import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent / "main.py"
SPEC = importlib.util.spec_from_file_location("json_to_csv_main", MODULE_PATH)
json_to_csv_main = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(json_to_csv_main)


class TestJsonToCsv(unittest.TestCase):
    def write_json(self, path, data):
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file)

    def read_csv(self, path):
        with open(path, "r", encoding="utf-8", newline="") as csv_file:
            return csv_file.read().replace("\r\n", "\n")

    def test_smallest_valid_input(self):
        """Source lines 18-21 establish the first keys as headers and values as rows."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "small.json"
            csv_path = Path(temp_dir) / "small.csv"
            self.write_json(json_path, [{"id": 1}])

            returned = json_to_csv_main.json_to_csv(json_path, csv_path)

            expected_return = str(csv_path)
            expected_csv = "id\n1\n"
            self.assertEqual(str(returned), expected_return)
            self.assertEqual(self.read_csv(csv_path), expected_csv)

    def test_ordinary_valid_input(self):
        """Source line 20 establishes that the first record's keys become the header."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "ordinary.json"
            csv_path = Path(temp_dir) / "ordinary.csv"
            data = [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
            self.write_json(json_path, data)

            json_to_csv_main.json_to_csv(json_path, csv_path)

            expected_csv = "name,age\nAlice,30\nBob,25\n"
            self.assertEqual(self.read_csv(csv_path), expected_csv)

    def test_repeatability_and_input_isolation(self):
        """Source lines 12-15 use separate read and write file state with proper file closing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_json = Path(temp_dir) / "fixture.json"
            first_csv = Path(temp_dir) / "first.csv"
            second_csv = Path(temp_dir) / "second.csv"
            intervening_json = Path(temp_dir) / "intervening.json"
            intervening_csv = Path(temp_dir) / "intervening.csv"

            self.write_json(fixture_json, [{"item": "book", "qty": 3}])
            self.write_json(intervening_json, [{"x": 100, "y": 200, "z": 300}])

            json_to_csv_main.json_to_csv(fixture_json, first_csv)
            first_output = self.read_csv(first_csv)

            json_to_csv_main.json_to_csv(intervening_json, intervening_csv)
            intervening_output = self.read_csv(intervening_csv)

            json_to_csv_main.json_to_csv(fixture_json, second_csv)
            second_output = self.read_csv(second_csv)

            expected_fixture = "item,qty\nbook,3\n"
            expected_intervening = "x,y,z\n100,200,300\n"
            self.assertEqual(first_output, expected_fixture)
            self.assertEqual(intervening_output, expected_intervening)
            self.assertEqual(second_output, expected_fixture)
            self.assertEqual(first_output, second_output)


if __name__ == "__main__":
    unittest.main()
