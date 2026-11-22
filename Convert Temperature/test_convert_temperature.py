import ast
import io
import runpy
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SOURCE_PATH = Path(__file__).resolve().parent / "Convert Temperature.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def load_from_cel():
    function_node = None
    for node in TREE.body:
        if isinstance(node, ast.FunctionDef) and node.name == "from_cel":
            function_node = node
            break

    if function_node is None:
        raise AssertionError("from_cel() was not found")

    module = ast.Module(body=[function_node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(SOURCE_PATH), "exec"), namespace)
    return namespace["from_cel"]


from_cel = load_from_cel()


class TestFromCelsiusExamples(unittest.TestCase):
    def test_import_does_not_start_interactive_menu(self):
        """Main calls get_temp only under __name__=='__main__' in the final source."""
        with patch("builtins.input",
                   side_effect=AssertionError("interactive CLI started during import")):
            runpy.run_path(str(SOURCE_PATH), run_name="convert_temperature_test")

    def test_smallest_valid_temperature_to_kelvin(self):
        """Source line 22 accepts a float, and source line 29 handles Kelvin choice b."""
        output = io.StringIO()

        with patch("builtins.input", side_effect=["-273.15", "b"]), \
                redirect_stdout(output):
            from_cel()

        expected_intermediate = -273.15 + 273.15
        expected_output = "The temperature is: 0.0 K\n"
        self.assertEqual(expected_intermediate, 0.0)
        self.assertEqual(output.getvalue(), expected_output)

    def test_ordinary_temperature_to_fahrenheit(self):
        """Source line 25 handles Fahrenheit choice a and line 26 performs x*(9/5)+32."""
        output = io.StringIO()

        with patch("builtins.input", side_effect=["25", "a"]), \
                redirect_stdout(output):
            from_cel()

        expected_intermediate = 25 * (9 / 5)
        expected_final = expected_intermediate + 32
        expected_output = "The temperature is: 77.0 °F\n"
        self.assertEqual(expected_intermediate, 45.0)
        self.assertEqual(expected_final, 77.0)
        self.assertEqual(output.getvalue(), expected_output)


if __name__ == "__main__":
    unittest.main()
