import hashlib
import importlib.util
import json
import platform
import random
import statistics
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPOSITORY_ROOT / "Website Blocker" / "mac" / "Website_Blocker.py"
REPORT_PATH = Path(__file__).resolve().parent / "results.json"
INPUT_SIZES = (100, 1000, 5000)
REPETITIONS = 5
BASE_SEED = 29035
BLOCKED_LINE_RATE = 0.2


def load_website_blocker():
    module_spec = importlib.util.spec_from_file_location(
        "_r35_t029_website_blocker",
        SOURCE_PATH,
    )
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"Unable to load {SOURCE_PATH}")

    module = importlib.util.module_from_spec(module_spec)
    with patch("builtins.open", side_effect=AssertionError("unexpected file I/O")):
        module_spec.loader.exec_module(module)
    return module


WEBSITE_BLOCKER = load_website_blocker()
BENCHMARK_OBSERVATIONS = []


class CountedLine(str):
    def __new__(cls, value, counter):
        instance = super().__new__(cls, value)
        instance.counter = counter
        return instance

    def __contains__(self, value):
        self.counter["substring_checks"] += 1
        return super().__contains__(value)


def make_input(size, seed):
    generator = random.Random(seed)
    lines = []
    expected_lines = []
    for index in range(size):
        if generator.random() < BLOCKED_LINE_RATE:
            website = generator.choice(WEBSITE_BLOCKER.website_list)
            line = f"127.0.0.1 {website}\n"
        else:
            line = (
                f"192.0.2.{index % 254 + 1} "
                f"host-{index}-{generator.randrange(1_000_000)}.example.test\n"
            )
            expected_lines.append(line)
        lines.append(line)
    return lines, expected_lines


def digest_lines(lines):
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


class WebsiteBlockerChecks(unittest.TestCase):
    def test_removes_matching_lines_and_preserves_input(self):
        original_lines = [
            "127.0.0.1 localhost\n",
            "127.0.0.1 www.facebook.com\n",
            "192.0.2.10 example.test\n",
            "192.0.2.11 dub119.mail.live.com\n",
        ]
        input_lines = list(original_lines)
        expected = [
            "127.0.0.1 localhost\n",
            "192.0.2.10 example.test\n",
        ]

        with patch("builtins.open", side_effect=AssertionError("unexpected file I/O")):
            actual = WEBSITE_BLOCKER.remove_blocked_websites(input_lines)

        self.assertEqual(actual, expected)
        self.assertEqual(input_lines, original_lines)

    def test_fixed_seed_operation_counts_and_outputs(self):
        measurements = []
        for size in INPUT_SIZES:
            repetitions = []
            for repetition in range(REPETITIONS):
                seed = BASE_SEED + size * 10 + repetition
                raw_lines, expected_lines = make_input(size, seed)
                input_digest = digest_lines(raw_lines)
                counter = {"substring_checks": 0}
                counted_lines = [CountedLine(line, counter) for line in raw_lines]

                with patch(
                    "builtins.open",
                    side_effect=AssertionError("unexpected file I/O"),
                ):
                    actual_lines = WEBSITE_BLOCKER.remove_blocked_websites(
                        counted_lines
                    )

                actual_text = [str(line) for line in actual_lines]
                expected_result = {
                    "line_count": len(expected_lines),
                    "sha256": digest_lines(expected_lines),
                }
                actual_result = {
                    "line_count": len(actual_text),
                    "sha256": digest_lines(actual_text),
                }
                repetition_result = {
                    "repetition": repetition + 1,
                    "input": {
                        "line_count": size,
                        "seed": seed,
                        "sha256": input_digest,
                        "blocked_line_count": size - len(expected_lines),
                    },
                    "expected": expected_result,
                    "actual": actual_result,
                    "substring_checks": counter["substring_checks"],
                }
                repetitions.append(repetition_result)
                BENCHMARK_OBSERVATIONS.append(
                    {
                        "size": size,
                        **repetition_result,
                    }
                )

                self.assertEqual(actual_text, expected_lines)
                self.assertEqual([str(line) for line in counted_lines], raw_lines)

            counts = [result["substring_checks"] for result in repetitions]
            measurements.append(
                {
                    "input_size_lines": size,
                    "repetitions": repetitions,
                    "substring_checks": {
                        "median": statistics.median(counts),
                        "range_min": min(counts),
                        "range_max": max(counts),
                    },
                }
            )

        self.__class__.measurements = measurements


def write_report(result):
    git_version = subprocess.run(
        ["git", "--version"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    report = {
        "command": "python3 work/R35-T029/check.py",
        "source_contract_before_changes": {
            "module": "Website Blocker/mac/Website_Blocker.py",
            "public_inputs": (
                "No callable public API; script uses current time, the configured "
                "website list, and /etc/hosts contents"
            ),
            "result": (
                "Runs indefinitely; prints during work hours and otherwise returns "
                "implicitly after rewriting the hosts file"
            ),
            "mutation_behavior": (
                "Appends missing redirect entries during work hours; outside work "
                "hours removes matching host lines and truncates the file"
            ),
            "external_dependencies": (
                "Python datetime, built-in file I/O on /etc/hosts, stdout, and "
                "root privileges; no third-party package"
            ),
            "pre_change_status": (
                "The source did not compile: an unexpected indentation on line 1, "
                "with additional HTML-escaped Python tokens"
            ),
        },
        "implemented_helper": {
            "public_input": "a sequence of host-file lines",
            "result": "new list containing lines without any configured website",
            "mutation_behavior": "does not mutate the input sequence",
            "external_io": "none",
        },
        "input_size_definition": "number of host-file lines",
        "measurement_method": (
            "Count actual substring membership checks; the six-domain list is "
            "fixed, so operation counts avoid timer overhead"
        ),
        "workload": {
            "sizes": list(INPUT_SIZES),
            "repetitions_per_size": REPETITIONS,
            "base_seed": BASE_SEED,
            "blocked_line_rate": BLOCKED_LINE_RATE,
            "input_reconstruction": (
                "Each fresh fixture is reproducible from its recorded seed and "
                "the generator in check.py"
            ),
            "output_validation": (
                "Expected line lists are checked after each helper invocation; "
                "the recorded digest and line count must match"
            ),
        },
        "test_configuration": (
            "Python standard-library unittest; the repository has no root "
            "pytest/pyproject test configuration"
        ),
        "tool_versions": {
            "python": platform.python_version(),
            "git": git_version,
            "test_runner": "unittest (Python standard library)",
        },
        "tests_run": result.testsRun,
        "nonzero_test_count": result.testsRun > 0,
        "successful": result.wasSuccessful() and result.testsRun > 0,
        "failures": [test.id() for test, _ in result.failures],
        "errors": [test.id() for test, _ in result.errors],
        "benchmark": getattr(WebsiteBlockerChecks, "measurements", []),
        "repetitions": BENCHMARK_OBSERVATIONS,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(WebsiteBlockerChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    write_report(result)
    if result.testsRun == 0 or not result.wasSuccessful():
        return 1
    print(f"Focused tests run: {result.testsRun}")
    print(f"Results saved to {REPORT_PATH.relative_to(REPOSITORY_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
