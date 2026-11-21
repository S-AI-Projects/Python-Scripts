import re
import shlex
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TIMER_TESTS = REPOSITORY_ROOT / "Pomodoro Timer" / "tests"
TEST_COMMAND = [
    sys.executable,
    "-m",
    "unittest",
    "discover",
    "-s",
    str(TIMER_TESTS),
    "-p",
    "test_windows_timer.py",
    "-v",
]


def main():
    print(f"Command: {shlex.join(TEST_COMMAND)}", flush=True)
    result = subprocess.run(
        TEST_COMMAND,
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    output = result.stdout + result.stderr
    summary = re.search(r"^Ran (\d+) tests? in ", output, re.MULTILINE)

    if summary is None:
        print("Could not determine the focused test count.", file=sys.stderr)
        return result.returncode or 1

    test_count = int(summary.group(1))
    print(f"Focused tests run: {test_count}")
    if result.returncode:
        return result.returncode
    if test_count == 0:
        print("No focused tests were discovered.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
