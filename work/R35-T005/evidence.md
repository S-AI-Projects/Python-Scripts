# R35-T005 Evidence

## Student Details
- **Student Name**: Nitesh Kumar
- **URN**: e26b07f0629
- **Task ID**: R35-T005 (Issue #5)
- **Repository**: S-AI-Projects/Python-Scripts
- **Assigned working branch**: student/e26b07f0629/R35-T005

## Target Item
- **Module**: `JSON to YAML/json_to_yaml.py`
- **Target Functions**: `json_to_yaml`, `convert_json_to_yaml`, `main`
- **Precondition Anchors**:
  - `import json`
  - `import yaml`
  - `Usage: json2yaml.py <sourcefile.json> [target_file.yaml]`
  - `"ERROR: " + ... + " not found"`
  - `"ERROR: " + ... + " already exists"`

## Observable Dependencies Analysis
1. **In-Memory Core (`json_to_yaml`)**:
   - External dependencies: **None exists**.
   - Input: Python dictionary, list, or primitive.
   - Output: Serialized YAML string.
   - Mutation: Pure function; leaves input data structures unmodified.
2. **File Seam (`convert_json_to_yaml`)**:
   - Dependencies: Filesystem reading (`source_path`) and writing (`target_path`).
   - Seam: Parameterized dependency injection with safe defaults preserving caller compatibility.
3. **CLI Interface (`main`)**:
   - Dependencies: `sys.argv` (injected via `argv` parameter), `sys.stdout`.

## Repeatability and Input Isolation Proof
The repeatability invariant dictates that repeated executions in fresh isolated states and after intervening operations must produce bit-for-bit identical outputs without altering input state:
- **Run 1 (Fresh isolated state)**:
  `json_to_yaml(ordinary_input, sort_keys=False)` -> matches expected output.
- **Run 2 (Consecutive execution)**:
  `json_to_yaml(ordinary_input, sort_keys=False)` == `Run 1` (Bitwise identical).
- **Intervening Execution**:
  Converted `{"tool": "checker", "iterations": 50, "valid": True}`.
- **Run 3 (Post-intervening execution)**:
  `json_to_yaml(ordinary_input, sort_keys=False)` == `Run 1` (Bitwise identical, confirming prior state does not leak or alter subsequent executions).
- **Input Immutability**:
  `ordinary_input` verified identical to its pre-execution deep copy.

## Tool Versions
- **Python**: 3.15.0
- **Platform**: macOS (Darwin arm64)
- **pyyaml**: 6.0.4
- **Git Branch**: `student/e26b07f0629/R35-T005`

## Test Results and Evidence

### 1. Smallest Supported Input
- **Input**: `{}`
- **Expected Output**: `"{}\n"`
- **Actual Output**: `"{}\n"`
- **Status**: **PASS**

### 2. Ordinary Valid Input
- **Input**:
  ```json
  {
    "name": "Python-Scripts",
    "version": 1,
    "active": true,
    "tags": ["python", "scripts"]
  }
  ```
- **Expected Output**:
  ```yaml
  name: Python-Scripts
  version: 1
  active: true
  tags:
  - python
  - scripts
  ```
- **Actual Output**: Matches expected YAML byte-for-byte -> **PASS**

### 3. Native Test Runner Execution
- **Command**: `python3 -m unittest discover -s 'JSON to YAML' -p 'test_*.py' -v`
- **Result**: Ran 6 tests in 0.002s — OK (0 failures, 0 errors)
- **Status**: **PASS**

### 4. Failure Propagation Proof
- **Command**: `FORCE_WRONG=1 python3 work/R35-T005/check.py`
- **Output**: `FAIL: Smallest input mismatch: expected 'WRONG_OUTPUT\n', got '{}\n'`
- **Exit Code**: `1` (Non-zero exit on assertion failure verified)
- **Status**: **PASS**
