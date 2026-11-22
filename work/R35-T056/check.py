"""Run only the mocked post_tweet behavioral checks and propagate failures."""

import re
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMMAND = [
    "python3",
    "-m",
    "unittest",
    "discover",
    "-s",
    "work/R35-T056",
    "-p",
    "post_tweet_checks.py",
    "-v",
]


def main():
    print(f"Command: {shlex.join(COMMAND)}", flush=True)
    result = subprocess.run(
        COMMAND,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout, end="")

    match = re.search(r"^Ran (\d+) tests? in ", result.stdout, re.MULTILINE)
    if match is None or int(match.group(1)) == 0:
        print("Focused check did not execute any tests.", file=sys.stderr)
        return result.returncode or 1
    if result.returncode != 0:
        return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
