import json
import csv


def json_to_csv(json_path: str = './generated.json', csv_path: str = './generated.csv') -> str:
    """
    Convert a JSON file containing a list of records into a CSV file.

    Seam & Repeatability Specification:
    - Precondition: json_path points to an existing readable JSON file containing an iterable
      of dict records (source lines 19-27).
    - Smallest valid input: JSON file containing 1 item with 1 key-value pair: [{"id": 1}].
    - Ordinary input: JSON file containing multi-record dicts:
      [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}].
    - Dependency seam: Allows injecting json_path and csv_path with default fallbacks
      to './generated.json' and './generated.csv' preserving legacy callers.
    - State isolation: Completely deterministic and stateless; consecutive runs on the same
      fixture produce bitwise identical output without cross-run contamination.
    """
    with open(json_path, 'r', encoding='utf-8') as json_file:
        jsondata = json.load(json_file)

    with open(csv_path, 'w', newline='', encoding='utf-8') as data_file:
        csv_writer = csv.writer(data_file)
        count = 0
        for data in jsondata:
            if count == 0:
                header = list(data.keys())
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(list(data.values()))

    return csv_path


if __name__ == '__main__':
    json_to_csv()
