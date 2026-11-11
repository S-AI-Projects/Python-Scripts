import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import os
import glob as glob_module

# Ensure requests is available
try:
    import requests
except ImportError:
    for p in glob_module.glob(os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "lib", "python*", "site-packages")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import requests

sys.path.insert(0, os.path.dirname(__file__))
import insta_down


class TestConnectionRefactor(unittest.TestCase):
    @patch("requests.get")
    def test_smallest_valid_input(self, mock_get):
        # Smallest input: minimal URL and timeout
        # Preconditions established at insta_down.py lines 20-35
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            res = insta_down.connection(url="http://127.0.0.1", timeout=1)

        self.assertTrue(res)
        self.assertIn("You're connected to internet", captured_out.getvalue())
        mock_get.assert_called_once_with("http://127.0.0.1", timeout=1)

    @patch("requests.get")
    def test_ordinary_valid_input(self, mock_get):
        # Ordinary default input: http://www.google.com/, timeout=5
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            res = insta_down.connection(url="http://www.google.com/", timeout=5)

        self.assertTrue(res)
        self.assertIn("You're connected to internet", captured_out.getvalue())
        mock_get.assert_called_once_with("http://www.google.com/", timeout=5)

    @patch("requests.get")
    def test_http_error_handling(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        http_err = requests.HTTPError(response=mock_resp)
        mock_get.return_value.raise_for_status.side_effect = http_err

        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            res = insta_down.connection("http://example.com/err", timeout=2)

        self.assertFalse(res)
        self.assertIn("Checking internet connection failed, status code 503.", captured_out.getvalue())

    @patch("requests.get")
    def test_connection_error_handling(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            res = insta_down.connection()

        self.assertFalse(res)
        self.assertIn("No internet connection available.", captured_out.getvalue())


if __name__ == "__main__":
    unittest.main()
