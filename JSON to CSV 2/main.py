import json
import csv


def json_to_csv(json_path="./generated.json", csv_path="./generated.csv"):
    """
    Convert a JSON list into CSV using separate input and output paths.

    Source lines 11-16 establish that the first record supplies the header
    and each record supplies values in the same key order.
    """
    with open(json_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)

        for index, data in enumerate(json_data):
            if index == 0:
                csv_writer.writerow(data.keys())
            csv_writer.writerow(data.values())

    return csv_path


if __name__ == "__main__":
    json_to_csv()
