"""
Focused boundary regression tests for Pizza Order (order.py).

Preconditions and source anchors:
- Precondition anchor 1: pizza_lst = [] (order.py line 33)
- Precondition anchor 2: pizza_lst_current = [] (order.py line 34)
- Precondition anchor 3: list_order_yes (order.py line 37)
- Precondition anchor 4: list_order_no (order.py line 38)
- Precondition anchor 5: TOPPINGS tuple (order.py line 39)
- Precondition anchor 6: size validation in ['S', 'M', 'L', 'XL']
"""

import io
import os
import sys
import unittest
from unittest.mock import patch

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import order


class TestPizzaOrderBoundaries(unittest.TestCase):
    """Test suite asserting supported boundary behaviors of Pizza Order."""

    def setUp(self):
        # Reset module-level lists before each test
        order.pizza_lst = []
        order.pizza_lst_current = []

    def test_precondition_anchors(self):
        """Verify baseline data anchors exist in order.py."""
        source_path = os.path.join(MODULE_DIR, "order.py")
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("pizza_lst = []", content)
        self.assertIn("pizza_lst_current = []", content)
        self.assertIn("list_order_yes", content)
        self.assertIn("list_order_no", content)
        self.assertIn("TOPPINGS", content)

    def test_smallest_valid_input_empty_order_boundary(self):
        """
        Smallest valid input boundary: user declines ordering immediately ('No').
        Boundary: 0 pizzas ordered.
        Source anchor: pizza_lst = [] (order.py line 33)
        """
        inputs = iter(["No"])
        result = order.order_pizzas(input_func=lambda _: next(inputs), print_func=lambda *a, **k: None)
        self.assertEqual(result, [])
        self.assertEqual(order.pizza_lst, [])
        self.assertEqual(order.pizza_lst_current, [])

    def test_smallest_valid_pizza_boundary(self):
        """
        Smallest valid single pizza boundary: size 'S' with 0 toppings ('X').
        Boundary: 1 pizza, minimal size 'S', minimal toppings (0).
        """
        inputs = iter(["Yes", "S", "X", "No"])
        result = order.order_pizzas(input_func=lambda _: next(inputs), print_func=lambda *a, **k: None)
        expected = [("S", [])]
        self.assertEqual(result, expected)
        self.assertEqual(order.pizza_lst, expected)

    def test_ordinary_valid_input(self):
        """
        Ordinary valid input: 1 medium pizza ('M') with 2 standard toppings ('PEPPERONI', 'OLIVE').
        """
        inputs = iter(["Yes", "M", "PEPPERONI", "OLIVE", "X", "No"])
        result = order.order_pizzas(input_func=lambda _: next(inputs), print_func=lambda *a, **k: None)
        expected = [("M", ["PEPPERONI", "OLIVE"])]
        self.assertEqual(result, expected)
        self.assertEqual(order.pizza_lst, expected)

    def test_topping_fee_threshold_boundary_3_toppings(self):
        """
        Topping boundary test (side 1): Exactly 3 toppings (upper threshold without extra fee).
        """
        inputs = iter(["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "X", "No"])
        result = order.order_pizzas(input_func=lambda _: next(inputs), print_func=lambda *a, **k: None)
        expected = [("S", ["ONION", "TOMATO", "MUSHROOM"])]
        self.assertEqual(result, expected)
        self.assertEqual(len(result[0][1]), 3)

    def test_topping_fee_threshold_boundary_4_toppings(self):
        """
        Topping boundary test (side 2): Exactly 4 toppings (lower threshold incurring extra fee).
        """
        inputs = iter(["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "OLIVE", "X", "No"])
        result = order.order_pizzas(input_func=lambda _: next(inputs), print_func=lambda *a, **k: None)
        expected = [("S", ["ONION", "TOMATO", "MUSHROOM", "OLIVE"])]
        self.assertEqual(result, expected)
        self.assertEqual(len(result[0][1]), 4)

    def test_upper_size_boundary_XL(self):
        """
        Size boundary test: Maximum supported size 'XL'.
        """
        inputs = iter(["Yes", "XL", "BACON", "X", "No"])
        result = order.order_pizzas(input_func=lambda _: next(inputs), print_func=lambda *a, **k: None)
        expected = [("XL", ["BACON"])]
        self.assertEqual(result, expected)

    def test_invalid_input_recovery_boundary(self):
        """
        Test that invalid inputs outside the supported domain are reprompted and rejected.
        - Invalid order prompt: 'MAYBE' -> recovered with 'Yes'
        - Invalid size: 'TINY' -> recovered with 'M'
        - Invalid topping: 'CHOCOLATE' -> recovered with 'HAM'
        - Invalid continue prompt: 'PERHAPS' -> recovered with 'No'
        """
        inputs = iter(["MAYBE", "Yes", "TINY", "M", "CHOCOLATE", "HAM", "X", "PERHAPS", "No"])
        result = order.order_pizzas(input_func=lambda _: next(inputs), print_func=lambda *a, **k: None)
        expected = [("M", ["HAM"])]
        self.assertEqual(result, expected)

    def test_list_sentinel_command(self):
        """
        Control sentinel 'LIST': Displays available toppings without adding to toppings list.
        """
        captured = []
        inputs = iter(["Yes", "S", "LIST", "SPINACH", "X", "No"])
        result = order.order_pizzas(
            input_func=lambda _: next(inputs),
            print_func=lambda *a, **k: captured.append(a)
        )
        expected = [("S", ["SPINACH"])]
        self.assertEqual(result, expected)
        # Check that 'LIST' appeared in output prints
        self.assertTrue(any("LIST" in str(arg) for arg in captured))


if __name__ == "__main__":
    unittest.main()
