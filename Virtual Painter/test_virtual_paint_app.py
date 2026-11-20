import unittest
import sys
import os

# Ensure target directory is in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import virtual_paint_app as vpa


def mutant_getTool(x):
    """
    Deliberate plausible one-line mutation: changes strict `<` to `<=` at boundary x = 50 + ml.
    """
    if x <= 50 + vpa.ml:  # Mutation: < changed to <=
        return "line"
    elif x < 100 + vpa.ml:
        return "rectangle"
    elif x < 150 + vpa.ml:
        return "draw"
    elif x < 200 + vpa.ml:
        return "circle"
    else:
        return "erase"


class TestVirtualPainterMutationResistance(unittest.TestCase):
    """Mutation-resistant and boundary regression tests for getTool."""

    def test_anchors(self):
        """
        Verify source fixture / data anchors:
        max_x, max_y = 250+ml, 50 | prevx, prevy = 0,0
        """
        self.assertEqual((vpa.max_x, vpa.max_y), (400, 50))
        self.assertEqual((vpa.prevx, vpa.prevy), (0, 0))

    def test_smallest_valid_input(self):
        """
        Smallest valid input inside toolbar: x = 151 (just above ml = 150).
        Preconditions established by line 75: x > ml.
        Expected: 'line'.
        """
        self.assertEqual(vpa.getTool(151), "line")

    def test_ordinary_valid_input(self):
        """
        Ordinary valid input inside toolbar: x = 275 (midpoint of [150, 400]).
        Falls in [250, 300) -> expected 'draw'.
        """
        self.assertEqual(vpa.getTool(275), "draw")

    def test_boundary_values_across_all_tools(self):
        """
        Verify all boundary transitions:
        - [151, 199] -> 'line'
        - [200, 249] -> 'rectangle'
        - [250, 299] -> 'draw'
        - [300, 349] -> 'circle'
        - [350, 400] -> 'erase'
        """
        self.assertEqual(vpa.getTool(199), "line")
        self.assertEqual(vpa.getTool(200), "rectangle")
        self.assertEqual(vpa.getTool(249), "rectangle")
        self.assertEqual(vpa.getTool(250), "draw")
        self.assertEqual(vpa.getTool(299), "draw")
        self.assertEqual(vpa.getTool(300), "circle")
        self.assertEqual(vpa.getTool(349), "circle")
        self.assertEqual(vpa.getTool(350), "erase")

    def test_mutation_detection_at_boundary_200(self):
        """
        Verify that original implementation passes and mutant fails at boundary x = 200.
        """
        # Original: x = 200 is not < 200, correctly advances to 'rectangle'
        self.assertEqual(vpa.getTool(200), "rectangle")

        # Mutant: x = 200 satisfies <= 200, incorrectly returns 'line'
        self.assertNotEqual(mutant_getTool(200), "rectangle")
        self.assertEqual(mutant_getTool(200), "line")


if __name__ == "__main__":
    unittest.main()
