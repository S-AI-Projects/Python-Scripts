import unittest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import main as j2c


class TestJsonToCsvRepeatable(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_smallest_valid_input(self):
        # Smallest input: 1 record, 1 field: [{"id": 1}]
        json_file = os.path.join(self.temp_dir.name, "small.json")
        csv_file = os.path.join(self.temp_dir.name, "small.csv")

        data = [{"id": 1}]
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        j2c.json_to_csv(json_file, csv_file)
        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()

        expected = "id\n1\n"
        self.assertEqual(content.replace("\r\n", "\n"), expected)

    def test_ordinary_valid_input(self):
        json_file = os.path.join(self.temp_dir.name, "ordinary.json")
        csv_file = os.path.join(self.temp_dir.name, "ordinary.csv")

        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        j2c.json_to_csv(json_file, csv_file)
        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()

        expected = "name,age\nAlice,30\nBob,25\n"
        self.assertEqual(content.replace("\r\n", "\n"), expected)

    def test_repeatability_and_input_isolation(self):
        # Step 3: Run the same fixture twice in fresh isolated state and once after another valid input;
        # assert that earlier runs cannot alter the later result.
        f1_json = os.path.join(self.temp_dir.name, "f1.json")
        f1_csv1 = os.path.join(self.temp_dir.name, "f1_run1.csv")
        f1_csv2 = os.path.join(self.temp_dir.name, "f1_run2.csv")
        intervening_json = os.path.join(self.temp_dir.name, "inter.json")
        intervening_csv = os.path.join(self.temp_dir.name, "inter.csv")

        data_fixture = [{"key": "val", "count": 10}]
        with open(f1_json, "w", encoding="utf-8") as f:
            json.dump(data_fixture, f)

        data_intervening = [{"diff_a": 1, "diff_b": 2, "diff_c": 3}]
        with open(intervening_json, "w", encoding="utf-8") as f:
            json.dump(data_intervening, f)

        # Run 1 on fixture
        j2c.json_to_csv(f1_json, f1_csv1)
        with open(f1_csv1, "r", encoding="utf-8") as f:
            res1 = f.read()

        # Intervening run on different data
        j2c.json_to_csv(intervening_json, intervening_csv)

        # Run 2 on fixture
        j2c.json_to_csv(f1_json, f1_csv2)
        with open(f1_csv2, "r", encoding="utf-8") as f:
            res2 = f.read()

        # Both runs on fixture must be bitwise identical
        self.assertEqual(res1, res2)
        self.assertEqual(res1.replace("\r\n", "\n"), "key,count\nval,10\n")


if __name__ == "__main__":
    unittest.main()
