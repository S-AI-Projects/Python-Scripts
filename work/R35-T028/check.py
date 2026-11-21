import contextlib
import importlib.util
import io
import json
import platform
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPOSITORY_ROOT / "URL Shortener" / "urlshortener.py"
REPORT_PATH = Path(__file__).resolve().parent / "results.json"
REQUEST_URL_PREFIX = "http://tinyurl.com/api-create.php?url="


def load_urlshortener():
    requests_stub = types.ModuleType("requests")
    requests_stub.get = Mock(
        return_value=types.SimpleNamespace(
            status_code=200,
            text="https://tinyurl.com/imported",
        )
    )
    module_spec = importlib.util.spec_from_file_location(
        "_r35_t028_urlshortener",
        SOURCE_PATH,
    )
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"Unable to load {SOURCE_PATH}")

    module = importlib.util.module_from_spec(module_spec)
    with patch.dict(sys.modules, {"requests": requests_stub}):
        with contextlib.redirect_stdout(io.StringIO()):
            module_spec.loader.exec_module(module)
    return module


URLSHORTENER = load_urlshortener()
OBSERVATIONS = []


class TinyUrlShortenerTests(unittest.TestCase):
    def test_non_200_returns_none_and_next_call_succeeds(self):
        long_url = ""
        original_input = long_url
        failed_response = types.SimpleNamespace(status_code=503, text="Unavailable")
        successful_response = types.SimpleNamespace(
            status_code=200,
            text="https://tinyurl.com/after-failure",
        )
        get = Mock(side_effect=[failed_response, successful_response])

        with patch.object(URLSHORTENER.requests, "get", get):
            failure_result = URLSHORTENER.shorten_url_with_tinyurl(long_url)
            input_after_failure = long_url
            success_result = URLSHORTENER.shorten_url_with_tinyurl(long_url)

        actual = {
            "failure_result": failure_result,
            "input_after_failure": input_after_failure,
            "input_identity_preserved": input_after_failure is original_input,
            "success_result": success_result,
            "requests_get_calls": [call.args[0] for call in get.call_args_list],
        }
        expected = {
            "failure_result": None,
            "input_after_failure": "",
            "input_identity_preserved": True,
            "success_result": "https://tinyurl.com/after-failure",
            "requests_get_calls": [REQUEST_URL_PREFIX, REQUEST_URL_PREFIX],
        }
        OBSERVATIONS.append(
            {
                "test": self.id(),
                "input": {
                    "long_url": long_url,
                    "failure_status_code": 503,
                    "success_status_code": 200,
                },
                "expected": expected,
                "actual": actual,
            }
        )

        self.assertIsNone(failure_result)
        self.assertEqual(input_after_failure, original_input)
        self.assertIs(input_after_failure, original_input)
        self.assertEqual(success_result, "https://tinyurl.com/after-failure")
        self.assertEqual(actual["requests_get_calls"], expected["requests_get_calls"])

    def test_200_returns_response_text(self):
        long_url = "https://example.com/"
        response_text = "https://tinyurl.com/example"
        get = Mock(
            return_value=types.SimpleNamespace(status_code=200, text=response_text)
        )

        with patch.object(URLSHORTENER.requests, "get", get):
            actual_result = URLSHORTENER.shorten_url_with_tinyurl(long_url)

        actual = {
            "result": actual_result,
            "input_after_call": long_url,
            "requests_get_calls": [call.args[0] for call in get.call_args_list],
        }
        expected = {
            "result": response_text,
            "input_after_call": long_url,
            "requests_get_calls": [REQUEST_URL_PREFIX + long_url],
        }
        OBSERVATIONS.append(
            {
                "test": self.id(),
                "input": {
                    "long_url": long_url,
                    "status_code": 200,
                    "response_text": response_text,
                },
                "expected": expected,
                "actual": actual,
            }
        )

        self.assertEqual(actual_result, response_text)
        self.assertEqual(long_url, actual["input_after_call"])
        self.assertEqual(actual["requests_get_calls"], expected["requests_get_calls"])


def write_report(result):
    git_version = subprocess.run(
        ["git", "--version"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    report = {
        "command": "python3 work/R35-T028/check.py",
        "source_contract": {
            "module": "URL Shortener/urlshortener.py",
            "public_input": "long_url (one string argument)",
            "successful_result": "response.text when response.status_code == 200",
            "non_200_result": "None",
            "caller_input_mutation": "none; the string argument is not modified",
            "external_dependency": (
                "requests.get; the module-level demo calls it on import, and "
                "the public function calls it once per invocation"
            ),
            "import_time_io": "the module-level request is mocked during import",
            "smallest_non_200_input": {
                "long_url": "",
                "mocked_status_code": 503,
                "expected_result": None,
            },
        },
        "test_configuration": (
            "Python standard-library unittest; the repository has no root "
            "pytest/pyproject test configuration"
        ),
        "tool_versions": {
            "python": platform.python_version(),
            "git": git_version,
            "test_runner": "unittest (Python standard library)",
            "requests_installed": importlib.util.find_spec("requests") is not None,
        },
        "tests_run": result.testsRun,
        "nonzero_test_count": result.testsRun > 0,
        "successful": result.wasSuccessful() and result.testsRun > 0,
        "failures": [test.id() for test, _ in result.failures],
        "errors": [test.id() for test, _ in result.errors],
        "cases": OBSERVATIONS,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TinyUrlShortenerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    write_report(result)
    if result.testsRun == 0 or not result.wasSuccessful():
        return 1
    print(f"Focused tests run: {result.testsRun}")
    print(f"Results saved to {REPORT_PATH.relative_to(REPOSITORY_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
