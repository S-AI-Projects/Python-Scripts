import importlib.util
import json
import platform
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = (
    REPOSITORY_ROOT / "Subnetting Calculator" / "subnetting_calculator.py"
)
REPORT_PATH = Path(__file__).resolve().parent / "results.json"
OBSERVATIONS = []


def load_module(module_path, module_name):
    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"Unable to load {module_path}")

    module = importlib.util.module_from_spec(module_spec)
    with (
        patch("builtins.input", side_effect=AssertionError("unexpected input")),
        patch("builtins.print", side_effect=AssertionError("unexpected output")),
    ):
        module_spec.loader.exec_module(module)
    return module


SUBNETTING_CALCULATOR = load_module(SOURCE_PATH, "_r35_t030_subnetting_calculator")


class SubnettingCalculatorChecks(unittest.TestCase):
    def test_calculates_a_30_network_without_mutating_inputs(self):
        ip_address = "192.0.2.130"
        subnet_mask = "255.255.255.252"
        original_inputs = (ip_address, subnet_mask)
        expected = {
            "IP Address": "192.0.2.130",
            "Subnet Mask": "255.255.255.252",
            "Network Address": "192.0.2.128",
            "Broadcast Address": "192.0.2.131",
            "Range of IP addresses": "192.0.2.128 - 192.0.2.131",
            "Usable Host IP Range": "192.0.2.129 - 192.0.2.130",
            "Total Hosts": 4,
            "Usable Hosts": 2,
        }

        actual = SUBNETTING_CALCULATOR.calculate_network_info(
            ip_address,
            subnet_mask,
        )
        observation = {
            "input": {
                "ip_address": ip_address,
                "subnet_mask": subnet_mask,
            },
            "expected": expected,
            "actual": actual,
            "inputs_after_call": [ip_address, subnet_mask],
        }
        OBSERVATIONS.append(
            {
                "check": self.id(),
                **observation,
            }
        )

        self.assertEqual(actual, expected)
        self.assertEqual((ip_address, subnet_mask), original_inputs)

    def test_temporary_boundary_mutant_is_detected_and_reduced(self):
        source = SOURCE_PATH.read_text(encoding="utf-8")
        original_condition = (
            'f"{first_usable_host} - {last_usable_host}" '
            'if usable_hosts > 0 else "N/A"'
        )
        mutant_condition = (
            'f"{first_usable_host} - {last_usable_host}" '
            'if usable_hosts >= 0 else "N/A"'
        )
        self.assertEqual(source.count(original_condition), 1)
        mutant_source = source.replace(original_condition, mutant_condition, 1)

        initial_input = ("192.0.2.0", "31")
        reduced_input = ("0.0.0.0", "32")
        with tempfile.TemporaryDirectory(prefix="r35-t030-mutant-") as directory:
            mutant_path = Path(directory) / "subnetting_calculator_mutant.py"
            mutant_path.write_text(mutant_source, encoding="utf-8")
            mutant_module = load_module(
                mutant_path,
                "_r35_t030_subnetting_calculator_mutant",
            )

            initial_original = SUBNETTING_CALCULATOR.calculate_network_info(
                *initial_input
            )
            initial_mutant = mutant_module.calculate_network_info(*initial_input)
            reduced_original = SUBNETTING_CALCULATOR.calculate_network_info(
                *reduced_input
            )
            reduced_mutant = mutant_module.calculate_network_info(*reduced_input)

        independently_expected = {
            "IP Address": "0.0.0.0",
            "Subnet Mask": "32",
            "Network Address": "0.0.0.0",
            "Broadcast Address": "0.0.0.0",
            "Range of IP addresses": "0.0.0.0 - 0.0.0.0",
            "Usable Host IP Range": "N/A",
            "Total Hosts": 1,
            "Usable Hosts": 0,
        }
        observation = {
            "mutation": {
                "original_condition": "usable_hosts > 0",
                "mutant_condition": "usable_hosts >= 0",
                "temporary_copy_only": True,
            },
            "initial_valid_input": {
                "ip_address": initial_input[0],
                "subnet_mask": initial_input[1],
            },
            "initial_results": {
                "original": initial_original,
                "mutant": initial_mutant,
            },
            "reduced_valid_input": {
                "ip_address": reduced_input[0],
                "subnet_mask": reduced_input[1],
                "reduction_reason": (
                    "A /32 is a valid one-address network, the smallest IPv4 "
                    "network size; the mutant still changes the result."
                ),
            },
            "independently_expected_reduced_result": independently_expected,
            "reduced_results": {
                "original": reduced_original,
                "mutant": reduced_mutant,
            },
        }
        OBSERVATIONS.append(
            {
                "check": self.id(),
                **observation,
            }
        )

        self.assertNotEqual(initial_original, initial_mutant)
        self.assertEqual(reduced_original, independently_expected)
        self.assertNotEqual(reduced_mutant, independently_expected)
        self.assertEqual(reduced_mutant["Usable Host IP Range"], "None - None")


def write_report(result):
    git_version = subprocess.run(
        ["git", "--version"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    report = {
        "command": "python3 work/R35-T030/check.py",
        "source_contract_before_changes": {
            "module": "Subnetting Calculator/subnetting_calculator.py",
            "public_inputs": "ip_address and subnet_mask strings",
            "result": (
                "a dictionary containing normalized network, broadcast, "
                "address-range, and host-count information"
            ),
            "mutation_behavior": (
                "calculate_network_info does not mutate either input; it returns "
                "a newly created dictionary"
            ),
            "external_dependencies": (
                "standard-library ipaddress only; the CLI main uses input() and "
                "print(), but the calculator function does not perform I/O"
            ),
        },
        "mutation_test": {
            "temporary_copy": True,
            "comparison_changed": "usable_hosts > 0 to usable_hosts >= 0",
            "initial_input": {
                "ip_address": "192.0.2.0",
                "subnet_mask": "31",
            },
            "reduced_input": {
                "ip_address": "0.0.0.0",
                "subnet_mask": "32",
            },
            "reduction": (
                "The reduced /32 network contains one address, the minimum "
                "possible IPv4 network size, and still distinguishes the mutant."
            ),
            "independent_expected_basis": (
                "IPv4 prefix arithmetic gives a /32 one total address; that "
                "address is both the network and broadcast address, leaving "
                "zero usable hosts and no usable-host range."
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
        "checks": OBSERVATIONS,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SubnettingCalculatorChecks
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    write_report(result)
    if result.testsRun == 0 or not result.wasSuccessful():
        return 1
    print(f"Focused tests run: {result.testsRun}")
    print(f"Results saved to {REPORT_PATH.relative_to(REPOSITORY_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
