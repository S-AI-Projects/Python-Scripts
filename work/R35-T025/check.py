import json
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = Path(__file__).resolve().parent
TEST_FILE = WORK_DIR / "test_text_recognition.py"
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
    "--rootdir",
    str(ROOT),
    str(TEST_FILE),
]


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
            r"\b(\d+)\s+(?:passed|failed|errors?|skipped|xfailed|xpassed)\b",
            output,
        )
    )

    cases_present = CASES_FILE.exists()
    case_failures = []
    if cases_present:
        evidence = json.loads(CASES_FILE.read_text(encoding="utf-8"))
        case_failures = [
            case["scenario"]
            for case in evidence["cases"]
            if case["actual"] != case["expected"]
        ]

    lines = [
        "Text Recognition focused verification",
        "======================================",
        f"Runner command: python3 work/R35-T025/check.py",
        f"Focused test command: {command_text}",
        "Test configuration: no repository-level pytest configuration exists; "
        "pytest defaults are used and collection is restricted to "
        "test_text_recognition.py.",
        f"Test result: exit {test_result.returncode}; {test_count} tests reported.",
        f"Input/result evidence: "
        f"{'present' if cases_present else 'missing'} at "
        "inputs_expected_actual.json.",
        f"Independent evidence mismatches: {len(case_failures)}"
        + (f" ({', '.join(case_failures)})" if case_failures else ""),
        "External I/O: requests, PIL image decoding, and Transformers model "
        "loading/inference are mocked; no network or model download is used.",
        f"Tool versions: Python {platform.python_version()}; "
        f"{tool_version([sys.executable, '-m', 'pytest', '--version'])}; "
        f"{tool_version(['git', '--version'])}; {platform.platform()}",
        "",
        "Focused pytest output",
        "----------------------",
        output.rstrip(),
        "",
    ]
    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")

    status = test_result.returncode
    if not test_count:
        print("No focused tests were reported.", file=sys.stderr)
        status = status or 1
    if not cases_present:
        print("Expected/actual evidence was not produced.", file=sys.stderr)
        status = status or 1
    if case_failures:
        print(
            "Expected/actual mismatch in: " + ", ".join(case_failures),
            file=sys.stderr,
        )
        status = status or 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
