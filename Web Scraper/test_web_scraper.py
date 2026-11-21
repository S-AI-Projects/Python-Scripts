"""
Focused regression unit tests for Web Scraper (Web_Scraper.py).

Preconditions and source anchors:
- Precondition 1 (Web_Scraper.py line 5): URL = "https://www.python.org/blogs/" default target URL.
- Precondition 2 (Web_Scraper.py line 8): requests.get(url) HTTP GET request.
- Precondition 3 (Web_Scraper.py line 11): BeautifulSoup(content, "html.parser") HTML parsing.
- Precondition 4 (Web_Scraper.py line 14): soup.find_all('h2', class_='blog-title') title tag selector.
- Precondition 5 (Web_Scraper.py line 17): display_blog_titles stdout formatting.
- Precondition 6 (Web_Scraper.py line 22): open(filename, 'w') persistent title writing.
"""

import io
import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Ensure the module can be imported from current directory
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import Web_Scraper


class TestWebScraperContract(unittest.TestCase):
    """Regression test suite locking down the contract of Web Scraper."""

    def setUp(self):
        # Fixture 1: Smallest valid input
        self.smallest_html = '<h2 class="blog-title">A</h2>'
        self.smallest_expected_titles = ["A"]
        self.smallest_expected_file = "A\n"

        # Fixture 2: Ordinary input with multiple items and surrounding markup
        self.ordinary_html = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head><title>Python Blogs</title></head>\n"
            "<body>\n"
            '  <div class="blog-posts">\n'
            '    <h2 class="blog-title">Python 3.12 Released</h2>\n'
            "    <p>Details about Python 3.12 release.</p>\n"
            '    <h2 class="blog-title">PSF Grants Overview</h2>\n'
            "    <p>Details about PSF grants.</p>\n"
            "  </div>\n"
            "</body>\n"
            "</html>"
        )
        self.ordinary_expected_titles = [
            "Python 3.12 Released",
            "PSF Grants Overview",
        ]
        self.ordinary_expected_file = "Python 3.12 Released\nPSF Grants Overview\n"

        # Fixture 3: Domain boundary with repeated values and empty titles
        self.boundary_html = (
            "<html><body>\n"
            '  <h2 class="blog-title">Duplicate Title</h2>\n'
            '  <h2 class="blog-title">  Duplicate Title  </h2>\n'
            '  <h2 class="blog-title"></h2>\n'
            "</body></html>"
        )
        self.boundary_expected_titles = [
            "Duplicate Title",
            "Duplicate Title",
            "",
        ]
        self.boundary_expected_file = "Duplicate Title\nDuplicate Title\n\n"

    def test_precondition_anchors_present(self):
        """Verify baseline source anchors are present in Web_Scraper.py."""
        source_path = os.path.join(MODULE_DIR, "Web_Scraper.py")
        with open(source_path, "r", encoding="utf-8") as f:
            source = f.read()

        self.assertIn('URL = "https://www.python.org/blogs/"', source)
        self.assertIn("requests.get(", source)
        self.assertIn('"html.parser"', source)
        self.assertIn("blog-title", source)
        self.assertIn("blog_titles.txt", source)

    def test_smallest_valid_input_returned_value(self):
        """
        Test returned value for smallest valid input separately from mutation.
        Precondition: Web_Scraper.py line 14 establishes h2.blog-title extraction.
        """
        titles = Web_Scraper.extract_blog_titles(self.smallest_html)
        self.assertEqual(titles, self.smallest_expected_titles)

    def test_smallest_valid_input_file_mutation(self):
        """
        Test observable file mutation for smallest valid input separately from return value.
        Precondition: Web_Scraper.py line 22 establishes open(filename, 'w') writing.
        """
        m_open = mock_open()
        with patch("builtins.open", m_open):
            Web_Scraper.save_blog_titles(self.smallest_expected_titles, filename="blog_titles.txt")

        m_open.assert_called_once_with("blog_titles.txt", "w", encoding="utf-8")
        handle = m_open()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(written_data, self.smallest_expected_file)

    def test_ordinary_input_returned_value(self):
        """
        Test returned value for ordinary input separately from mutation.
        Precondition: Web_Scraper.py lines 11-14 parse and extract multiple titles.
        """
        titles = Web_Scraper.extract_blog_titles(self.ordinary_html)
        self.assertEqual(titles, self.ordinary_expected_titles)

    def test_ordinary_input_file_mutation(self):
        """
        Test observable file mutation for ordinary input separately from return value.
        Precondition: Web_Scraper.py lines 22-24 write each title with newline.
        """
        m_open = mock_open()
        with patch("builtins.open", m_open):
            Web_Scraper.save_blog_titles(self.ordinary_expected_titles, filename="test_ordinary.txt")

        m_open.assert_called_once_with("test_ordinary.txt", "w", encoding="utf-8")
        handle = m_open()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(written_data, self.ordinary_expected_file)

    def test_ordinary_input_stdout_mutation(self):
        """
        Test observable stdout mutation separately from return value.
        Precondition: Web_Scraper.py lines 17-19 format and print numbered titles.
        """
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            Web_Scraper.display_blog_titles(self.ordinary_expected_titles)

        output_str = captured_output.getvalue()
        self.assertIn("Python.org Blog Titles:", output_str)
        self.assertIn("1. Python 3.12 Released", output_str)
        self.assertIn("2. PSF Grants Overview", output_str)

    def test_boundary_repeated_values_and_empty_title(self):
        """
        Test repeated-value domain boundary and whitespace stripping.
        Precondition: Web_Scraper.py line 14 extracts all occurrences stripped.
        """
        titles = Web_Scraper.extract_blog_titles(self.boundary_html)
        self.assertEqual(titles, self.boundary_expected_titles)

    def test_main_orchestration_with_mocked_io(self):
        """
        Test full main() pipeline with mocked external network and file I/O.
        Preconditions:
        - Web_Scraper.py line 8 (requests.get)
        - Web_Scraper.py line 14 (extract_blog_titles)
        - Web_Scraper.py line 22 (save_blog_titles)
        """
        mock_response = MagicMock()
        mock_response.content = self.ordinary_html.encode("utf-8")

        m_open = mock_open()
        with patch("Web_Scraper.fetch_webpage", return_value=mock_response) as mock_fetch, \
             patch("builtins.open", m_open), \
             patch("sys.stdout", io.StringIO()):
            result = Web_Scraper.main(url="https://mocked.python.org/blogs", filename="custom_titles.txt")

        mock_fetch.assert_called_once_with("https://mocked.python.org/blogs")
        self.assertEqual(result, self.ordinary_expected_titles)
        m_open.assert_called_once_with("custom_titles.txt", "w", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
