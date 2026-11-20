import importlib.util
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = ROOT / "work" / "R35-T024"
TEST_FILE = ROOT / "JSON to CSV 1" / "tests" / "test_pyscript.py"
RESULTS_FILE = WORK_DIR / "results.txt"
CASES_FILE = WORK_DIR / "inputs_expected_actual.json"
TEST_COMMAND = [
    sys.executable,
    "-m",
    "pytest",
    "-q",
    "--tb=short",
    "-p",
    "no:cacheprovider",
    str(TEST_FILE),
]
SOURCE_PRECONDITIONS = (
    "JSON to CSV 1/code/pyscript.py:7 loads JSON; :9 selects emp_details; "
    ":21 iterates records; :25 and :30 use each record's keys and values"
)


def tool_version(command):
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return f"unavailable (exit {result.returncode}): {result.stderr.strip()}"
    return (result.stdout or result.stderr).strip()


def load_test_module():
    spec = importlib.util.spec_from_file_location("test_pyscript", TEST_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load focused tests from {TEST_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    command_text = shlex.join(TEST_COMMAND)
    print(f"Focused test command: {command_text}", flush=True)
    test_result = subprocess.run(
        TEST_COMMAND,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stdout.write(test_result.stdout)
    sys.stderr.write(test_result.stderr)
    output = test_result.stdout + test_result.stderr
    test_count = sum(
        int(count)
        for count in re.findall(
            r"\b(\d+) (?:passed|failed|errors?|skipped|xfailed|xpassed)\b",
            output,
        )
    )
    print(f"Focused tests reported: {test_count}")

    test_module = load_test_module()
    cases = [
        ("minimal", test_module.MINIMAL_INPUT, test_module.MINIMAL_EXPECTED),
        ("ordinary", test_module.ORDINARY_INPUT, test_module.ORDINARY_EXPECTED),
        *test_module.make_generated_cases(),
    ]
    case_results = []
    for case_name, input_text, expected in cases:
        actual = test_module.run_script(input_text)
        case_results.append(
            {
                "name": case_name,
                "input_json": input_text,
                "expected_csv": expected,
                "actual_csv": actual,
                "passed": actual == expected,
                "precondition_source": SOURCE_PRECONDITIONS,
            }
        )
    CASES_FILE.write_text(
        json.dumps(
            {
                "fixed_seed": 35024,
                "generated_case_count": 128,
                "case_count": len(case_results),
                "cases": case_results,
            },
            indent=2,
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
    )

    status = test_result.returncode
    if not test_count:
        print("No focused tests were reported.", file=sys.stderr)
        status = status or 1
    case_failures = [
        case["name"] for case in case_results if not case["passed"]
    ]
    if case_failures:
        print(
            "Expected/actual output mismatch in: " + ", ".join(case_failures),
            file=sys.stderr,
        )
        status = status or 1

    pre_change_results = RESULTS_FILE.read_text(encoding="utf-8")
    pre_change_results = pre_change_results.split(
        "\nPost-change validation\n", maxsplit=1
    )[0].rstrip()
    RESULTS_FILE.write_text(
        "\n".join(
            [
                pre_change_results,
                "",
                "Post-change validation",
                "-----------------------",
                f"Runner command: python3 work/R35-T024/check.py",
                f"Focused test command: {command_text}",
                f"Result: exit {test_result.returncode}; {test_count} test cases reported",
                f"Tool versions: Python {sys.version.split()[0]}; "
                f"{tool_version([sys.executable, '-m', 'pytest', '--version'])}; "
                f"{tool_version(['git', '--version'])}",
                "I/O: data.json and data_file.csv are mocked by the tests.",
                f"Case results: {len(case_results)} cases, including 128 fixed-seed "
                "generated valid cases; inputs and expected/actual CSV are in "
                "inputs_expected_actual.json.",
                f"Independent case mismatches: {len(case_failures)}",
                "Test output",
                "-----------",
                output.rstrip(),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
