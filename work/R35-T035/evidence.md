# R35-T035 Evidence

## Previous PR #65

PR #65 was closed and proposed a callable `json_to_csv` function, repeatability
tests, a main guard, and evidence. Those files were not present locally.
The existing source had fixed relative paths and opened both files at import.

## Existing behavior and correction

Before this change, the script:

- Read `./generated.json` at source line 4.
- Wrote `./generated.csv` at source line 7.
- Used the first record's keys as the header at source line 13.
- Wrote every record's values at source line 16.

This behavior was preserved through `json_to_csv()`. The source now has:

- A `json_to_csv(json_path, csv_path)` seam.
- Default paths `./generated.json` and `./generated.csv`.
- Proper `with open` file handling.
- A `if __name__ == "__main__"` guard.

## Literal inputs and expected outputs

The precondition at final source lines 18-21 is that JSON is a list of
dictionary records. The first dictionary supplies CSV header names and each
dictionary supplies row values. The input and output paths are established by
the `json_to_csv(json_path, csv_path)` seam at line 5.

| Case | Literal JSON input | Expected CSV |
|---|---|---|
| Smallest | `[{"id": 1}]` | `id\n1\n` |
| Ordinary | `[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]` | `name,age\nAlice,30\nBob,25\n` |

Repeatability fixture:

1. Run fixture `[{"item": "book", "qty": 3}]`.
2. Run intervening valid input `[{"x": 100, "y": 200, "z": 300}]`.
3. Run fixture `[{"item": "book", "qty": 3}]` again.

Expected fixture output: `item,qty\nbook,3\n`
Expected intervening output: `x,y,z\n100,200,300\n`
Repeatability result: first and second fixture outputs are identical.

## Tool versions

- Python: 3.15.2
- Dependency: no third-party packages are required; `json` and `csv` are
  Python standard-library modules.

## Baseline

Before implementation, importing `main.py` failed with:
`FileNotFoundError: ./generated.json`.

This proved that import-time file I/O prevented isolated tests.

## Final command

- Command: `python3 work/R35-T035/check.py`
- unittest test methods: 3
- Result: PASS
