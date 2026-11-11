# R35-T035 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T035 (Issue #35)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T035

## Target Item
- Module: `JSON to CSV 2/main.py`
- Target Function: `json_to_csv(json_path='./generated.json', csv_path='./generated.csv')`
- Source line precondition: Lines 19-27 (JSON reading, CSV creation, header and record mapping)

## Dependency Seam Analysis
- External Dependencies: File I/O (`open` for reading JSON and writing CSV).
- Seam Introduced: `json_to_csv(json_path, csv_path)` parameterizes file locations with defaults maintaining backward compatibility for legacy callers.
- State Isolation: Function is completely deterministic and stateless with zero cross-call mutation or leakage.

## Tool Versions
- Python: 3.15.2
- OS: macOS (Darwin)

## Verification Results
1. Smallest Valid Input:
   - Input: JSON file containing `[{"id": 1}]`
   - Expected Output: `"id\n1\n"`
   - Actual Output: `"id\n1\n"`
   - Result: PASS

2. Ordinary Valid Input:
   - Input: JSON file containing `[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]`
   - Expected Output: `"name,age\nAlice,30\nBob,25\n"`
   - Actual Output: `"name,age\nAlice,30\nBob,25\n"`
   - Result: PASS

3. Repeatability and Input Isolation Check:
   - Run 1 on fixture `[{"item": "book", "qty": 3}]`
   - Intervening Run on `[{"x": 100, "y": 200, "z": 300}]`
   - Run 2 on fixture `[{"item": "book", "qty": 3}]`
   - Assert Run 1 == Run 2 bitwise.
   - Result: PASS (Exact bitwise match)

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T035/check.py`
   - Output: `FAIL: Expected 'WRONG\n', got 'id\n1\n'`
   - Exit code: 1
