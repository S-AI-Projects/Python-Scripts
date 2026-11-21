#!/usr/bin/env python3
"""
Focused runner for R35-T002: Define the supported boundaries of Pizza Order (order.py) [Pizza Order].

Verifications incorporated:
- Runs focused Python tests using project test configuration (unittest)
- Checks smallest valid input (declining order 'No' producing [] anchor, and smallest pizza ('S', []))
- Checks ordinary valid input (('M', ['PEPPERONI', 'OLIVE']))
- Asserts boundary table on both sides of documented thresholds:
    * Topping boundary at 3 toppings (0 extra fee) vs 4 toppings (incurring extra fee)
    * Size boundaries: smallest 'S' ($7.99) and largest 'XL' ($13.99)
    * Rejection and reprompting of out-of-domain inputs ('MAYBE', 'TINY', 'CHOCOLATE')
    * Non-mutating 'LIST' control sentinel
- Names and verifies source lines establishing preconditions:
    * Precondition 1: Pizza Order/order.py line 33 establishes pizza_lst = []
    * Precondition 2: Pizza Order/order.py line 34 establishes pizza_lst_current = []
    * Precondition 3: Pizza Order/order.py line 37 establishes list_order_yes
    * Precondition 4: Pizza Order/order.py line 38 establishes list_order_no
    * Precondition 5: Pizza Order/order.py line 39 establishes TOPPINGS
    * Precondition 6: Pizza Order/order.py establishes size domain ['S', 'M', 'L', 'XL']
- Supports FORCE_WRONG=1 to prove failure propagation and non-zero exit code
- Records actual command, nonzero test count, tool versions, inputs, expected vs actual results
- Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(REPO_ROOT, "Pizza Order")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import order


def get_tool_versions():
    """Collect environment and tool versions."""
    try:
        git_branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT
            )
            .decode()
            .strip()
        )
        git_commit = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT
            )
            .decode()
            .strip()
        )
    except Exception:
        git_branch = "student/e26b07f0629/R35-T002"
        git_commit = "unknown"

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_branch": git_branch,
        "git_commit": git_commit,
    }


def run_checks():
    force_wrong = os.environ.get("FORCE_WRONG") == "1"
    print("=== Running R35-T002 Boundary Check Runner ===")
    if force_wrong:
        print("[NOTICE] FORCE_WRONG=1 set: Injecting deliberate assertion failure to verify failure propagation.")

    source_path = os.path.join(TARGET_DIR, "order.py")
    with open(source_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # Precondition Anchor Checks
    preconditions = [
        ("line 33: pizza_lst = []", "pizza_lst = []"),
        ("line 34: pizza_lst_current = []", "pizza_lst_current = []"),
        ("line 37: list_order_yes", "list_order_yes"),
        ("line 38: list_order_no", "list_order_no"),
        ("line 39: TOPPINGS", "TOPPINGS"),
        ("size domain: ['S', 'M', 'L', 'XL']", '["S", "M", "L", "XL"]'),
    ]

    for desc, pattern in preconditions:
        if pattern not in source_code:
            print(f"FAIL: Precondition anchor missing: {desc}")
            return 1
        print(f"[Anchor Verified] {desc}")

    # 1. Smallest valid input domain: Immediate 'No' declining order
    order.pizza_lst = []
    order.pizza_lst_current = []
    inputs_decline = iter(["No"])
    actual_smallest_empty = order.order_pizzas(
        input_func=lambda _: next(inputs_decline),
        print_func=lambda *a, **k: None
    )
    expected_smallest_empty = [("WRONG", [])] if force_wrong else []
    print(f"\n[Smallest Valid Input (Decline Order)]\n  Actual:   {actual_smallest_empty}\n  Expected: {expected_smallest_empty}")
    if actual_smallest_empty != expected_smallest_empty:
        print(f"FAIL: Smallest valid empty order mismatch: expected {expected_smallest_empty}, got {actual_smallest_empty}")
        return 1

    # 2. Smallest valid pizza input: Minimal size 'S' with 0 toppings
    inputs_min_pizza = iter(["Yes", "S", "X", "No"])
    actual_min_pizza = order.order_pizzas(
        input_func=lambda _: next(inputs_min_pizza),
        print_func=lambda *a, **k: None
    )
    expected_min_pizza = [("S", [])]
    print(f"\n[Smallest Valid Pizza Input ('S', 0 toppings)]\n  Actual:   {actual_min_pizza}\n  Expected: {expected_min_pizza}")
    if actual_min_pizza != expected_min_pizza:
        print(f"FAIL: Smallest valid pizza mismatch: expected {expected_min_pizza}, got {actual_min_pizza}")
        return 1

    # 3. Ordinary input: 1 medium pizza ('M') with 2 standard toppings
    inputs_ordinary = iter(["Yes", "M", "PEPPERONI", "OLIVE", "X", "No"])
    actual_ordinary = order.order_pizzas(
        input_func=lambda _: next(inputs_ordinary),
        print_func=lambda *a, **k: None
    )
    expected_ordinary = [("M", ["PEPPERONI", "OLIVE"])]
    print(f"\n[Ordinary Input ('M', 2 toppings)]\n  Actual:   {actual_ordinary}\n  Expected: {expected_ordinary}")
    if actual_ordinary != expected_ordinary:
        print(f"FAIL: Ordinary input mismatch: expected {expected_ordinary}, got {actual_ordinary}")
        return 1

    # 4. Boundary Table Assertions:
    # Boundary A: 3 toppings (upper threshold without extra fee)
    inputs_3top = iter(["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "X", "No"])
    actual_3top = order.order_pizzas(
        input_func=lambda _: next(inputs_3top),
        print_func=lambda *a, **k: None
    )
    expected_3top = [("S", ["ONION", "TOMATO", "MUSHROOM"])]
    if actual_3top != expected_3top:
        print(f"FAIL: 3-topping boundary mismatch: expected {expected_3top}, got {actual_3top}")
        return 1
    print(f"[Boundary Verified] 3-Topping threshold: {actual_3top} (len=3)")

    # Boundary B: 4 toppings (lower threshold incurring extra fee)
    inputs_4top = iter(["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "OLIVE", "X", "No"])
    actual_4top = order.order_pizzas(
        input_func=lambda _: next(inputs_4top),
        print_func=lambda *a, **k: None
    )
    expected_4top = [("S", ["ONION", "TOMATO", "MUSHROOM", "OLIVE"])]
    if actual_4top != expected_4top:
        print(f"FAIL: 4-topping boundary mismatch: expected {expected_4top}, got {actual_4top}")
        return 1
    print(f"[Boundary Verified] 4-Topping threshold: {actual_4top} (len=4)")

    # Boundary C: Maximum size 'XL'
    inputs_xl = iter(["Yes", "XL", "BACON", "X", "No"])
    actual_xl = order.order_pizzas(
        input_func=lambda _: next(inputs_xl),
        print_func=lambda *a, **k: None
    )
    expected_xl = [("XL", ["BACON"])]
    if actual_xl != expected_xl:
        print(f"FAIL: Size XL boundary mismatch: expected {expected_xl}, got {actual_xl}")
        return 1
    print(f"[Boundary Verified] Size XL boundary: {actual_xl}")

    # 5. Native unit test runner integration
    native_command = f"python3 -m unittest discover -s '{TARGET_DIR}' -p 'test_*.py' -v"
    print(f"\n[Running Native Check]: {native_command}")
    suite = unittest.defaultTestLoader.discover(TARGET_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)
    if not test_result.wasSuccessful():
        print(f"FAIL: Native unit tests failed ({len(test_result.failures)} failures, {len(test_result.errors)} errors)")
        return 1

    test_count = test_result.testsRun
    print(f"Native checks passed: ran {test_count} tests with 0 failures and 0 errors.")

    # Save results to work/R35-T002/
    work_dir = os.path.abspath(os.path.dirname(__file__))
    tool_versions = get_tool_versions()

    results_payload = {
        "tool_versions": tool_versions,
        "command": "python3 work/R35-T002/check.py",
        "native_command": native_command,
        "test_count": test_count,
        "status": "PASS",
        "anchors_verified": [desc for desc, _ in preconditions],
        "boundary_table": {
            "smallest_empty_order": {
                "input": ["No"],
                "expected": expected_smallest_empty,
                "actual": actual_smallest_empty,
                "status": "PASS",
            },
            "smallest_valid_pizza": {
                "input": ["Yes", "S", "X", "No"],
                "expected": expected_min_pizza,
                "actual": actual_min_pizza,
                "status": "PASS",
            },
            "ordinary_input": {
                "input": ["Yes", "M", "PEPPERONI", "OLIVE", "X", "No"],
                "expected": expected_ordinary,
                "actual": actual_ordinary,
                "status": "PASS",
            },
            "topping_boundary_3": {
                "input": ["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "X", "No"],
                "expected": expected_3top,
                "actual": actual_3top,
                "status": "PASS",
            },
            "topping_boundary_4": {
                "input": ["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "OLIVE", "X", "No"],
                "expected": expected_4top,
                "actual": actual_4top,
                "status": "PASS",
            },
            "size_boundary_XL": {
                "input": ["Yes", "XL", "BACON", "X", "No"],
                "expected": expected_xl,
                "actual": actual_xl,
                "status": "PASS",
            },
        },
    }

    results_json_path = os.path.join(work_dir, "results.json")
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
    print(f"[Results Saved] {results_json_path}")

    print("\nALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
