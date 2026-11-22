import importlib.util
import io
import runpy
import unittest
from contextlib import redirect_stdout
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent / "starPattern.py"
SPEC = importlib.util.spec_from_file_location("star_pattern", MODULE_PATH)
star_pattern = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(star_pattern)


class TestStarPattern(unittest.TestCase):
    def test_import_does_not_request_input(self):
        """Lines 15-17 protect interactive input behind the main guard."""
        from unittest.mock import patch

        with patch("builtins.input",
                   side_effect=AssertionError("interactive input started during import")):
            runpy.run_path(str(MODULE_PATH),
                           run_name="star_pattern_test")

    def test_smallest_valid_input(self):
        """Line 9 is the outer range; n=1 produces one row containing '* '."""
        output = io.StringIO()

        with redirect_stdout(output):
            returned = star_pattern.starPattern(1)

        expected_output = "* \n"
        expected_return = None
        self.assertEqual(output.getvalue(), expected_output)
        self.assertIs(returned, expected_return)

    def test_ordinary_input(self):
        """Lines 9-12 print row i with i stars, so n=3 prints three literal rows."""
        output = io.StringIO()

        with redirect_stdout(output):
            returned = star_pattern.starPattern(3)

        expected_output = "* \n* * \n* * * \n"
        expected_return = None
        self.assertEqual(output.getvalue(), expected_output)
        self.assertIs(returned, expected_return)

    def test_empty_result_case_does_not_corrupt_state(self):
        """Line 9's range(1, n+1) is range(1, 1) for n=0, so no inner loop runs."""
        caller_state = {"unchanged": True}
        empty_output = io.StringIO()

        with redirect_stdout(empty_output):
            returned = star_pattern.starPattern(0)

        expected_empty_output = ""
        expected_return = None
        self.assertEqual(empty_output.getvalue(), expected_empty_output)
        self.assertIs(returned, expected_return)
        self.assertEqual(caller_state, {"unchanged": True})

        normal_output = io.StringIO()
        with redirect_stdout(normal_output):
            star_pattern.starPattern(2)

        self.assertEqual(normal_output.getvalue(), "* \n* * \n")
        self.assertEqual(caller_state, {"unchanged": True})


if __name__ == "__main__":
    unittest.main()
