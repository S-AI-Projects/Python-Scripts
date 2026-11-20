import io
import json
import random
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "JSON to CSV 1" / "code" / "pyscript.py"

MINIMAL_INPUT = '{"emp_details":[{"name":"Ada"}]}'
MINIMAL_EXPECTED = "name\r\nAda\r\n"

ORDINARY_INPUT = (
    '{"emp_details":[{"name":"Ada","team":"Research"},'
    '{"team":"Engineering","name":"Lin"}]}'
)
ORDINARY_EXPECTED = (
    "name,team\r\n"
    "Ada,Research\r\n"
    "Lin,Engineering\r\n"
)

SOURCE_PRECONDITIONS = (
    "pyscript.py:7 loads JSON; :9 selects emp_details; "
    ":21 iterates records; :25 and :30 use each record's keys and values"
)


class CapturedOutput(io.StringIO):
    def close(self):
        self.flush()


def run_script(input_text):
    input_stream = io.StringIO(input_text)
    output_stream = CapturedOutput()

    def mocked_open(path, mode="r", *args, **kwargs):
        if path == "data.json" and mode == "r":
            return input_stream
        if path == "data_file.csv" and mode == "w":
            return output_stream
        raise AssertionError(f"Unexpected file access: {path!r} in {mode!r}")

    with patch("builtins.open", side_effect=mocked_open):
        runpy.run_path(str(SOURCE), run_name="__main__")

    return output_stream.getvalue()


def make_generated_cases():
    generator = random.Random(35024)
    fields = ("employee", "team", "office")

    for case_number in range(128):
        record_count = generator.randint(1, 4)
        records = []
        for _ in range(record_count):
            values = {
                "employee": f"emp{generator.randint(0, 9999)}",
                "team": f"team{generator.randint(0, 9999)}",
                "office": f"office{generator.randint(0, 9999)}",
            }
            field_order = generator.sample(fields, len(fields))
            records.append({field: values[field] for field in field_order})

        input_text = json.dumps(
            {"emp_details": records},
            separators=(",", ":"),
        )
        header = list(records[0])
        output_rows = [",".join(header)]
        output_rows.extend(
            ",".join(record[field] for field in header)
            for record in records
        )
        expected = "\r\n".join(output_rows) + "\r\n"
        yield (
            f"seed-35024-{case_number:03d}",
            input_text,
            expected,
        )


@pytest.mark.parametrize(
    ("case_name", "input_text", "expected"),
    [
        pytest.param(
            "minimal",
            MINIMAL_INPUT,
            MINIMAL_EXPECTED,
            id="minimal-pyscript.py-9-21-25-30",
        ),
        pytest.param(
            "ordinary",
            ORDINARY_INPUT,
            ORDINARY_EXPECTED,
            id="ordinary-pyscript.py-9-21-25-30",
        ),
        *[
            pytest.param(
                name,
                input_text,
                expected,
                id=f"{name}-pyscript.py-9-21-25-30",
            )
            for name, input_text, expected in make_generated_cases()
        ],
    ],
)
def test_json_employee_records_are_written_under_their_headers(
    case_name,
    input_text,
    expected,
):
    payload = json.loads(input_text)
    assert set(payload) == {"emp_details"}, SOURCE_PRECONDITIONS
    records = payload["emp_details"]
    assert records and all(isinstance(record, dict) for record in records), (
        SOURCE_PRECONDITIONS
    )
    assert all(set(record) == set(records[0]) for record in records), (
        SOURCE_PRECONDITIONS
    )

    actual = run_script(input_text)

    assert actual == expected, f"{case_name}: {SOURCE_PRECONDITIONS}"
