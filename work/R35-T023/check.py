import re
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "Selfie with Python" / "tests" / "test_selfie_with_python.py"
RESULTS_FILE = ROOT / "work" / "R35-T023" / "results.txt"
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


def tool_version(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        return f"unavailable (exit {result.returncode}): {result.stderr.strip()}"
    return (result.stdout or result.stderr).strip()


def main():
    command_text = shlex.join(TEST_COMMAND)
    print(f"Command: {command_text}", flush=True)
    result = subprocess.run(
        TEST_COMMAND,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    output = result.stdout + result.stderr
    counts = [
        int(count)
        for count in re.findall(r"\b(\d+) (?:passed|failed|error|skipped|xfailed|xpassed)\b", output)
    ]
    test_count = sum(counts)
    print(f"Focused tests run: {test_count}")

    status = result.returncode
    if not test_count:
        print("No focused tests were reported.", file=sys.stderr)
        status = status or 1

    RESULTS_FILE.write_text(
        "\n".join(
            [
                "R35-T023 focused selfie checks",
                "",
                "Tool versions",
                "-------------",
                f"Python: {sys.version.split()[0]}",
                f"Pytest: {tool_version([sys.executable, '-m', 'pytest', '--version'])}",
                f"Git: {tool_version(['git', '--version'])}",
                "OpenCV: mocked; no camera or OpenCV installation is required",
                "",
                "Observed module contract",
                "-------------------------",
                "Public inputs: no command-line or function arguments; the script "
                "waits 5 seconds, reads frames from camera index 0, and responds "
                "to Space (save) and Escape (exit).",
                "Result: no explicit Python return value; it prints status and "
                "writes Selfie_<n>.jpg files in the current working directory.",
                "Mutation and resources: the image counter is local to the run; "
                "saved JPEGs persist, and the camera/window are opened during "
                "execution. Before the fix, cam.release was referenced but not "
                "called; it is now called after the loop.",
                "Dependencies: OpenCV (cv2) for camera/window/image operations "
                "and the standard-library time module; tests mock both modules' "
                "external I/O.",
                "Test configuration: no repository-level pytest configuration "
                "was found; pytest was run against only the named test module.",
                "",
                "Pre-fix comparison",
                "-------------------",
                "All 21 focused cases failed only on camera release: expected "
                "1 release call, observed 0. This included all 20 terminated "
                "key sequences and the failed-frame path.",
                "",
                "Focused command",
                "---------------",
                "Runner invocation: python3 work/R35-T023/check.py",
                command_text,
                f"Result: exit {result.returncode}; {test_count} test cases reported",
                "",
                "Test output",
                "-----------",
                output.rstrip(),
                "",
                "Per-input expected and actual results are recorded in "
                "inputs_expected_actual.json (20 terminated key sequences and "
                "one failed-frame case).",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
