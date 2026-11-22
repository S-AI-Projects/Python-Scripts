import ast
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


SOURCE_PATH = Path(__file__).resolve().parent / "insta_down.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def load_connection():
    helper_node = None
    connection_node = None
    for node in TREE.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == "_print_http_error":
                helper_node = node
            if node.name == "connection":
                connection_node = node

    if helper_node is None or connection_node is None:
        raise AssertionError("connection() or _print_http_error() was not found")

    module = ast.Module(
        body=[helper_node, connection_node],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)

    namespace = {}
    exec(compile(module, str(SOURCE_PATH), "exec"), namespace)
    return namespace["connection"]


connection = load_connection()


class HTTPError(Exception):
    def __init__(self, status_code):
        super().__init__(status_code)
        self.response = SimpleNamespace(status_code=status_code)


class ConnectionError(Exception):
    pass


def requests_namespace(get_mock):
    return SimpleNamespace(
        get=get_mock,
        HTTPError=HTTPError,
        ConnectionError=ConnectionError,
    )


class TestConnection(unittest.TestCase):
    def test_smallest_valid_input_uses_defaults(self):
        """Line 21 establishes URL='http://www.google.com/' and timeout=5 defaults."""
        response = Mock()
        response.raise_for_status = Mock()
        get_mock = Mock(return_value=response)
        namespace = requests_namespace(get_mock)

        original_globals = connection.__globals__.copy()
        connection.__globals__["requests"] = namespace
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                actual = connection()
        finally:
            connection.__globals__.clear()
            connection.__globals__.update(original_globals)

        get_mock.assert_called_once_with(
            "http://www.google.com/",
            timeout=5,
        )
        response.raise_for_status.assert_called_once_with()
        self.assertIs(actual, True)
        self.assertEqual(output.getvalue(), "You're connected to internet\n\n")

    def test_ordinary_input_uses_explicit_url_and_timeout(self):
        """Line 23 establishes that explicit url and timeout are passed unchanged."""
        response = Mock()
        response.raise_for_status = Mock()
        get_mock = Mock(return_value=response)
        namespace = requests_namespace(get_mock)

        original_globals = connection.__globals__.copy()
        connection.__globals__["requests"] = namespace
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                actual = connection(
                    "https://example.com/check",
                    timeout=12,
                )
        finally:
            connection.__globals__.clear()
            connection.__globals__.update(original_globals)

        get_mock.assert_called_once_with(
            "https://example.com/check",
            timeout=12,
        )
        response.raise_for_status.assert_called_once_with()
        self.assertIs(actual, True)
        self.assertEqual(output.getvalue(), "You're connected to internet\n\n")

    def test_http_error_returns_false_and_prints_status(self):
        """Line 27 establishes HTTPError handling and a status-code message."""
        get_mock = Mock()
        get_mock.return_value.raise_for_status.side_effect = HTTPError(503)
        namespace = requests_namespace(get_mock)

        original_globals = connection.__globals__.copy()
        connection.__globals__["requests"] = namespace
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                actual = connection("https://example.com/status", 3)
        finally:
            connection.__globals__.clear()
            connection.__globals__.update(original_globals)

        get_mock.assert_called_once_with(
            "https://example.com/status",
            timeout=3,
        )
        self.assertIs(actual, False)
        self.assertEqual(
            output.getvalue(),
            "Checking internet connection failed, status code 503.\n",
        )

    def test_connection_error_returns_false_and_prints_message(self):
        """Line 29 establishes ConnectionError handling and the no-network message."""
        get_mock = Mock(side_effect=ConnectionError())
        namespace = requests_namespace(get_mock)

        original_globals = connection.__globals__.copy()
        connection.__globals__["requests"] = namespace
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                actual = connection("https://offline.example", 7)
        finally:
            connection.__globals__.clear()
            connection.__globals__.update(original_globals)

        get_mock.assert_called_once_with(
            "https://offline.example",
            timeout=7,
        )
        self.assertIs(actual, False)
        self.assertEqual(output.getvalue(), "No internet connection available.\n")


if __name__ == "__main__":
    unittest.main()
