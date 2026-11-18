import json
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = Path(__file__).with_name("notify_suite_test.py").resolve()
RESULTS_FILE = Path(__file__).with_name("check_results.json")


def run_version_command(command: list[str]) -> dict[str, object]:
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    return {
        "command": shlex.join(command),
        "exit_code": result.returncode,
        "output": (result.stdout + result.stderr).strip(),
    }


def write_results(results: dict[str, object]) -> None:
    RESULTS_FILE.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        str(TEST_FILE.relative_to(PROJECT_ROOT)),
    ]
    version_results = [
        run_version_command(["python3", "--version"]),
        run_version_command(["pytest", "--version"]),
    ]
    results: dict[str, object] = {
        "runner_command": "python3 work/R35-T022/check.py",
        "tool_versions": version_results,
        "test_command": shlex.join(command),
        "checks": [],
    }
    write_results(results)

    print(f"Running: {shlex.join(command)}", flush=True)
    test_result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    print(test_result.stdout, end="")
    print(test_result.stderr, end="", file=sys.stderr)

    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    results["test_result"] = {
        "exit_code": test_result.returncode,
        "stdout": test_result.stdout,
        "stderr": test_result.stderr,
    }
    write_results(results)
    if test_result.returncode != 0:
        return test_result.returncode
    return next(
        (int(version["exit_code"]) for version in version_results if version["exit_code"]),
        0,
    )


if __name__ == "__main__":
    raise SystemExit(main())
