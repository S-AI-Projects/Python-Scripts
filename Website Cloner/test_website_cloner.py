import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import runnable_example as cloner_ex


class TestWebsiteClonerExample(unittest.TestCase):
    """
    Focused tests verifying the runnable example for Website Cloner (index.html).
    Precondition source lines:
      - index.html:1 establishes HTML5 document
      - index.html:8 establishes PROXY SERVER title
      - index.html:18 establishes POST form action="/"
      - index.html:20 establishes input name="submitButton"
    """

    def test_html_form_preconditions(self):
        index_file = os.path.join(BASE_DIR, "index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("<title>PROXY SERVER</title>", content)
        self.assertIn('action="/"', content)
        self.assertIn('name="submitButton"', content)
        self.assertIn('type="submit"', content)

    def test_smallest_valid_input_example(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = cloner_ex.execute_clone_pipeline("example.com", tmpdir)
            self.assertEqual(res["extracted_url"], "example.com")
            self.assertEqual(res["normalized_url"], "https://example.com")
            self.assertEqual(res["project_name"], "example.com")
            self.assertEqual(res["redirect_location"], "/cloned_sites/example.com/index.html")
            self.assertTrue(os.path.isfile(res["cloned_index_path"]))

    def test_ordinary_valid_input_example(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = cloner_ex.execute_clone_pipeline("https://www.python.org", tmpdir)
            self.assertEqual(res["extracted_url"], "https://www.python.org")
            self.assertEqual(res["normalized_url"], "https://www.python.org")
            self.assertEqual(res["project_name"], "www.python.org")
            self.assertEqual(res["redirect_location"], "/cloned_sites/www.python.org/index.html")
            self.assertTrue(os.path.isfile(res["cloned_index_path"]))

    def test_normalize_edge_cases(self):
        self.assertEqual(cloner_ex.normalize_clone_url("http://insecure.org/"), "http://insecure.org")
        self.assertEqual(cloner_ex.normalize_clone_url("https://secure.org/"), "https://secure.org")
        self.assertEqual(cloner_ex.normalize_clone_url("test.io"), "https://test.io")

    def test_runnable_example_main(self):
        exit_code = cloner_ex.run_worked_examples()
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
