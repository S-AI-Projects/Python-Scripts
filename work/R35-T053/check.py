#!/usr/bin/env python3
"""Focused runner that executes Expense Tracker checks and propagates failures.

Native check incorporated: run focused Python tests using project test configuration;
import or invoke only the named module, with external I/O mocked.
Records actual command and nonzero test count.
Saves inputs, expected vs actual results, and tool versions in work/R35-T053/.
"""

import copy
import importlib
import io
import json
import os
import platform
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, call, patch

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))
EXPENSE_TRACKER_DIR = os.path.join(REPO_ROOT, "Expense Tracker")

if EXPENSE_TRACKER_DIR not in sys.path:
    sys.path.insert(0, EXPENSE_TRACKER_DIR)

import expense


def save_artifact(filename, data):
    """Save dictionary or string to file in WORK_DIR."""
    filepath = os.path.join(WORK_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, indent=2)
        else:
            f.write(str(data))
    return filepath


def record_tool_versions():
    """Record versions of python, git, platform, and unittest."""
    git_version = "unknown"
    try:
        git_res = subprocess.run(["git", "--version"], capture_output=True, text=True, check=False)
        git_version = git_res.stdout.strip()
    except Exception as e:
        git_version = str(e)

    versions = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "git_version": git_version,
        "test_framework": "unittest (Python standard library)",
    }
    save_artifact("tool_versions.json", versions)
    return versions


# 22 Small Valid Inputs covering distinct boundary and domain conditions
ENUMERATED_INPUTS = [
    {
        "id": "input_01_empty_db_empty_table",
        "description": "Empty database with an empty initial table",
        "db_rows": [],
        "initial_table": [],
    },
    {
        "id": "input_02_empty_db_stale_table",
        "description": "Empty database with stale existing rows in the table to verify deletion",
        "db_rows": [],
        "initial_table": [(999, "2026-01-01", "Old Vendor", "Stale Entry", 10.0, "Cash")],
    },
    {
        "id": "input_03_single_typical_record",
        "description": "Single typical expense record",
        "db_rows": [(1, "2026-11-01", "Supermarket", "Groceries", 45.50, "Cash")],
        "initial_table": [],
    },
    {
        "id": "input_04_zero_amount_expense",
        "description": "Expense with zero amount (free item or coupon)",
        "db_rows": [(2, "2026-11-02", "Community Center", "Free Workshop", 0.0, "Cash")],
        "initial_table": [],
    },
    {
        "id": "input_05_float_precision_cents",
        "description": "Expense with floating point precision cents",
        "db_rows": [(3, "2026-11-03", "Bakery", "Muffin and coffee", 7.89, "Credit Card")],
        "initial_table": [],
    },
    {
        "id": "input_06_large_transaction_amount",
        "description": "Expense with large monetary value",
        "db_rows": [(4, "2026-11-04", "Automotive Dealer", "Car Downpayment", 15000.0, "Cheque")],
        "initial_table": [],
    },
    {
        "id": "input_07_micro_expense",
        "description": "Micro-expense under 1.0 unit",
        "db_rows": [(5, "2026-11-05", "Newsstand", "Single Gum", 0.25, "Debit Card")],
        "initial_table": [],
    },
    {
        "id": "input_08_negative_amount_refund",
        "description": "Negative amount representing return refund or credit",
        "db_rows": [(6, "2026-11-06", "Retailer", "Item Return Refund", -29.99, "Credit Card")],
        "initial_table": [],
    },
    {
        "id": "input_09_special_characters_payee",
        "description": "Payee name containing apostrophes, ampersands, hyphens",
        "db_rows": [(7, "2026-11-07", "O'Connor & Sons - Hardware", "Tools", 62.40, "Debit Card")],
        "initial_table": [],
    },
    {
        "id": "input_10_special_characters_description",
        "description": "Description with punctuation, parentheses, percentages, quotes",
        "db_rows": [(8, "2026-11-08", "Stationery Store", "Pens (black, 0.5mm); notebooks #2 & clips!", 18.00, "Cash")],
        "initial_table": [],
    },
    {
        "id": "input_11_unicode_and_emojis",
        "description": "Unicode characters and emojis in payee and description",
        "db_rows": [(9, "2026-11-09", "Café Central ☕", "Matcha latte 🍵 & croissant 🥐", 12.50, "Google Pay")],
        "initial_table": [],
    },
    {
        "id": "input_12_empty_payee",
        "description": "Empty string payee name",
        "db_rows": [(10, "2026-11-10", "", "Anonymous donation", 50.00, "Cash")],
        "initial_table": [],
    },
    {
        "id": "input_13_empty_description",
        "description": "Empty string description",
        "db_rows": [(11, "2026-11-11", "Utility Electric", "", 94.30, "Razorpay")],
        "initial_table": [],
    },
    {
        "id": "input_14_whitespace_fields",
        "description": "Whitespace-only strings in payee and description",
        "db_rows": [(12, "2026-11-12", "   ", "   ", 5.00, "Cash")],
        "initial_table": [],
    },
    {
        "id": "input_15_all_payment_modes",
        "description": "All 7 standard payment modes represented across rows",
        "db_rows": [
            (13, "2026-11-13", "Vendor 1", "Item 1", 10.0, "Cash"),
            (14, "2026-11-13", "Vendor 2", "Item 2", 20.0, "Cheque"),
            (15, "2026-11-13", "Vendor 3", "Item 3", 30.0, "Credit Card"),
            (16, "2026-11-13", "Vendor 4", "Item 4", 40.0, "Debit Card"),
            (17, "2026-11-13", "Vendor 5", "Item 5", 50.0, "Paytm"),
            (18, "2026-11-13", "Vendor 6", "Item 6", 60.0, "Google Pay"),
            (19, "2026-11-13", "Vendor 7", "Item 7", 70.0, "Razorpay"),
        ],
        "initial_table": [],
    },
    {
        "id": "input_16_table_mutation_with_multiple_stale_items",
        "description": "Multiple DB records with table having multiple stale items that must be cleared",
        "db_rows": [
            (20, "2026-11-14", "Pharmacy", "Medicine", 22.0, "Cash"),
            (21, "2026-11-14", "Taxi", "Ride", 14.5, "Paytm"),
        ],
        "initial_table": [
            (991, "2025-01-01", "Old 1", "Old Desc 1", 1.0, "Cash"),
            (992, "2025-01-02", "Old 2", "Old Desc 2", 2.0, "Cash"),
        ],
    },
    {
        "id": "input_17_duplicate_payees_same_date",
        "description": "Duplicate payees and dates with different descriptions and amounts",
        "db_rows": [
            (22, "2026-11-15", "Coffee Shop", "Morning Espresso", 3.50, "Cash"),
            (23, "2026-11-15", "Coffee Shop", "Afternoon Cold Brew", 4.50, "Cash"),
        ],
        "initial_table": [],
    },
    {
        "id": "input_18_duplicate_amounts_different_payees",
        "description": "Duplicate amounts across distinct payees",
        "db_rows": [
            (24, "2026-11-16", "Merchant A", "Subscription A", 9.99, "Credit Card"),
            (25, "2026-11-16", "Merchant B", "Subscription B", 9.99, "Credit Card"),
        ],
        "initial_table": [],
    },
    {
        "id": "input_19_date_format_variations",
        "description": "Various date format representations (ISO, slash, datetime timestamp)",
        "db_rows": [
            (26, "2026-11-17", "Vendor A", "ISO Date", 15.0, "Debit Card"),
            (27, "11/17/26", "Vendor B", "Slash Date", 25.0, "Credit Card"),
            (28, "2026-11-17 10:15:30", "Vendor C", "Timestamp", 35.0, "Cash"),
        ],
        "initial_table": [],
    },
    {
        "id": "input_20_non_sequential_ids",
        "description": "Five records with non-contiguous, arbitrary ID values",
        "db_rows": [
            (101, "2026-11-18", "P1", "D1", 11.0, "Cash"),
            (105, "2026-11-18", "P2", "D2", 22.0, "Cheque"),
            (110, "2026-11-18", "P3", "D3", 33.0, "Credit Card"),
            (115, "2026-11-18", "P4", "D4", 44.0, "Debit Card"),
            (120, "2026-11-18", "P5", "D5", 55.0, "Paytm"),
        ],
        "initial_table": [],
    },
    {
        "id": "input_21_ten_mixed_records_batch",
        "description": "Ten mixed records with diverse values and payment methods",
        "db_rows": [
            (201, "2026-11-19", "Alpha", "Item Alpha", 12.30, "Cash"),
            (202, "2026-11-19", "Beta", "Item Beta", 45.60, "Cheque"),
            (203, "2026-11-19", "Gamma", "Item Gamma", 78.90, "Credit Card"),
            (204, "2026-11-19", "Delta", "Item Delta", 10.00, "Debit Card"),
            (205, "2026-11-19", "Epsilon", "Item Epsilon", 25.50, "Paytm"),
            (206, "2026-11-19", "Zeta", "Item Zeta", 99.99, "Google Pay"),
            (207, "2026-11-19", "Eta", "Item Eta", 5.25, "Razorpay"),
            (208, "2026-11-19", "Theta", "Item Theta", 150.00, "Cash"),
            (209, "2026-11-19", "Iota", "Item Iota", 0.75, "Credit Card"),
            (210, "2026-11-19", "Kappa", "Item Kappa", 300.00, "Cheque"),
        ],
        "initial_table": [],
    },
    {
        "id": "input_22_twenty_five_records_high_volume",
        "description": "Twenty-five records simulating a full monthly expense register",
        "db_rows": [
            (301 + i, f"2026-11-{i+1:02d}", f"Vendor_{i+1}", f"Expense item #{i+1}", float(i * 10 + 5.5), ["Cash", "Credit Card", "Debit Card", "Paytm", "Google Pay"][i % 5])
            for i in range(25)
        ],
        "initial_table": [(888, "2020-01-01", "Old Stale", "Old Stale", 1.0, "Cash")],
    },
]


def record_inputs():
    """Record public inputs, contract, mutation behavior, oracle spec, and enumerated inputs."""
    inputs_data = {
        "module": "Expense Tracker/expense.py",
        "named_module": "expense",
        "function_under_audit": "list_all_expenses",
        "line_number": 9,
        "contract_analysis": {
            "public_inputs": {
                "direct_parameters": [
                    "conn (sqlite3.Connection, optional, default=None -> falls back to global connector)",
                    "tree (ttk.Treeview, optional, default=None -> falls back to global table)",
                ],
                "implicit_globals": [
                    "connector (sqlite3.Connection instance with ExpenseTracker table)",
                    "table (ttk.Treeview instance for rendering table rows)",
                ],
            },
            "result": {
                "return_type": "list of tuples",
                "content": "All fetched expense rows from ExpenseTracker table. (Original returned None; now returns data list for verification without breaking callers)",
            },
            "mutation_behavior": {
                "tree_mutation": "Calls tree.delete(*tree.get_children()) to purge prior display rows, then calls tree.insert('', END, values=values) for each DB row.",
                "database_mutation": "None (pure SELECT query; no commit or data modification).",
            },
            "external_dependencies": [
                "sqlite3 (SQLite database connection with ExpenseTracker schema)",
                "tkinter / tkinter.ttk.Treeview widget and Tk END constant",
                "top-level GUI mainloop and window creation (now encapsulated under __name__ == '__main__')",
            ],
        },
        "oracle_specification": {
            "description": "Independent oracle predicting final table state given DB records and initial table state.",
            "rule": "Table must be cleared of any pre-existing rows and populated with exactly the rows present in the database.",
            "order_handling": "SQL SELECT without ORDER BY explicitly leaves row ordering unspecified by relational theory. Comparison ignores row ordering by sorting multiset of rows by primary key ID and Date.",
        },
        "enumerated_inputs_count": len(ENUMERATED_INPUTS),
        "enumerated_inputs": ENUMERATED_INPUTS,
        "mocked_io": [
            "sqlite3 in-memory database (:memory:) replacing disk 'Expense Tracker.db'",
            "MockTreeview replacing tkinter.ttk.Treeview",
            "tkinter.messagebox (tb)",
            "tkcalendar.DateEntry",
            "sys.stdout",
        ],
    }
    save_artifact("inputs.json", inputs_data)
    return inputs_data


def run_native_checks():
    """Run focused Python tests using project test configuration (unittest)."""
    test_file = os.path.join(EXPENSE_TRACKER_DIR, "tests", "test_expense.py")
    test_cmd = [sys.executable, "-m", "unittest", test_file]
    actual_cmd_str = f"python3 -m unittest {os.path.relpath(test_file, REPO_ROOT)}"

    print(f"[RUNNER] Executing native test command: {actual_cmd_str}")
    proc = subprocess.run(
        test_cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    combined_output = proc.stdout + "\n" + proc.stderr
    print(combined_output)

    # Parse test count from unittest stderr output (e.g. "Ran 18 tests in 0.011s")
    test_count = 0
    for line in combined_output.splitlines():
        if line.startswith("Ran ") and "tests in" in line:
            parts = line.split()
            try:
                test_count = int(parts[1])
            except (IndexError, ValueError):
                pass
        elif line.startswith("Ran ") and "test in" in line:
            parts = line.split()
            try:
                test_count = int(parts[1])
            except (IndexError, ValueError):
                pass

    if proc.returncode != 0:
        raise RuntimeError(f"Native unit tests failed with exit code {proc.returncode}:\n{combined_output}")

    if test_count <= 0:
        raise RuntimeError(f"Native unit tests reported 0 tests executed. Command: {actual_cmd_str}")

    print(f"[RUNNER] Native tests passed successfully! Test count: {test_count}")
    return actual_cmd_str, test_count, combined_output


class MockTreeview:
    """In-memory mock for tkinter.ttk.Treeview widget."""

    def __init__(self, initial_items=None):
        self._items = {}
        self._counter = 1
        if initial_items:
            for item in initial_items:
                iid = f"item_{self._counter}"
                self._items[iid] = {"values": tuple(item)}
                self._counter += 1

    def get_children(self, item=None):
        return tuple(self._items.keys())

    def delete(self, *items):
        for item in items:
            self._items.pop(item, None)

    def insert(self, parent, index, iid=None, **kwargs):
        if iid is None:
            iid = f"item_{self._counter}"
            self._counter += 1
        self._items[iid] = kwargs
        return iid

    def get_all_values(self):
        return [tuple(data.get("values", ())) for data in self._items.values()]


def independent_oracle(db_rows, initial_table=None):
    """Oracle function that independently calculates the expected contents of the table."""
    return {
        "expected_cleared": True,
        "expected_rows": [tuple(r) for r in db_rows],
        "count": len(db_rows),
    }


def run_focused_checks():
    """Run direct programmatic assertion checks on expense module with mocked I/O."""
    import sqlite3

    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ExpenseTracker ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
        "Date DATETIME, "
        "Payee TEXT, "
        "Description TEXT, "
        "Amount FLOAT, "
        "ModeOfPayment TEXT)"
    )
    conn.commit()

    oracle_comparison_results = []
    direct_assertions = []

    # 1. Evaluate Oracle on all 22 enumerated inputs
    for case in ENUMERATED_INPUTS:
        conn.execute("DELETE FROM ExpenseTracker")
        for row in case["db_rows"]:
            conn.execute(
                "INSERT INTO ExpenseTracker (ID, Date, Payee, Description, Amount, ModeOfPayment) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                row,
            )
        conn.commit()

        mock_tree = MockTreeview(initial_items=case["initial_table"])
        oracle_res = independent_oracle(case["db_rows"], case["initial_table"])

        actual_ret = expense.list_all_expenses(conn=conn, tree=mock_tree)
        actual_tbl = mock_tree.get_all_values()

        # Sort to ignore unspecified order
        sorted_actual_tbl = sorted([tuple(r) for r in actual_tbl], key=lambda r: (r[0], str(r[1])))
        sorted_expected = sorted([tuple(r) for r in oracle_res["expected_rows"]], key=lambda r: (r[0], str(r[1])))

        assert sorted_actual_tbl == sorted_expected, (
            f"Oracle mismatch on {case['id']}: expected {sorted_expected}, got {sorted_actual_tbl}"
        )
        assert len(actual_tbl) == oracle_res["count"], (
            f"Count mismatch on {case['id']}: expected {oracle_res['count']}, got {len(actual_tbl)}"
        )

        oracle_comparison_results.append({
            "id": case["id"],
            "description": case["description"],
            "expected_count": oracle_res["count"],
            "actual_count": len(actual_tbl),
            "status": "PASS",
        })

    direct_assertions.append({
        "check": "oracle_comparison_all_22_inputs",
        "expected": "All 22 enumerated input cases match independent oracle ignoring row order",
        "actual": f"{len(oracle_comparison_results)}/22 passed",
        "status": "PASS",
    })

    # 2. Check mutation behavior: purge stale table items
    stale_tree = MockTreeview(initial_items=[(888, "2020-01-01", "Old", "Old", 1.0, "Cash")])
    assert len(stale_tree.get_children()) == 1, "Initial stale tree should have 1 item"
    conn.execute("DELETE FROM ExpenseTracker")
    expense.list_all_expenses(conn=conn, tree=stale_tree)
    assert len(stale_tree.get_children()) == 0, "Stale tree items should have been deleted"
    direct_assertions.append({
        "check": "table_purge_mutation_behavior",
        "expected": "Table items purged to 0 when DB is empty",
        "actual": "0 items in table",
        "status": "PASS",
    })

    # 3. Check safe import and global fallback
    assert expense.root is None, "expense.root should be None on clean import"
    assert expense.connector is None or isinstance(expense.connector, sqlite3.Connection), "expense.connector check"
    direct_assertions.append({
        "check": "safe_import_no_gui_side_effects",
        "expected": "expense.root is None, no GUI window or Tk mainloop blocked",
        "actual": "expense.root is None",
        "status": "PASS",
    })

    # 4. Check global fallback in list_all_expenses
    test_row = (42, "2026-11-22", "Test Payee", "Test Desc", 42.0, "Cash")
    conn.execute("DELETE FROM ExpenseTracker")
    conn.execute(
        "INSERT INTO ExpenseTracker (ID, Date, Payee, Description, Amount, ModeOfPayment) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        test_row,
    )
    conn.commit()

    global_tree = MockTreeview()
    with patch.object(expense, "connector", conn), patch.object(expense, "table", global_tree):
        ret = expense.list_all_expenses()
        assert ret == [test_row], f"Expected {[test_row]}, got {ret}"
        assert global_tree.get_all_values() == [test_row]

    direct_assertions.append({
        "check": "list_all_expenses_global_fallback",
        "expected": "list_all_expenses() uses global connector and table when none passed",
        "actual": f"Successfully retrieved {ret}",
        "status": "PASS",
    })

    conn.close()
    return oracle_comparison_results, direct_assertions


def main():
    print("[RUNNER] Starting work/R35-T053/check.py focused runner...")
    tool_versions = record_tool_versions()
    inputs_data = record_inputs()

    try:
        actual_cmd, test_count, test_output = run_native_checks()
        oracle_comparisons, direct_assertions = run_focused_checks()

        expected_vs_actual = {
            "baseline_mismatch_analysis": {
                "command": "python3 'Expense Tracker/expense.py'",
                "fixture_input": "Direct import or headless execution of original Expense Tracker/expense.py",
                "independent_expected": (
                    "Modular execution of list_all_expenses; clean import without GUI popups, "
                    "disk file mutations, or infinite Tk mainloop; headless compatibility when "
                    "Tkinter/_tkinter is unavailable; purge existing display items and insert all records."
                ),
                "actual_baseline_result": (
                    "ModuleNotFoundError: Unsupported platform for standard library module '_tkinter' on headless/macOS Python 3.15. "
                    "Top-level script unconditionally connects to 'Expense Tracker.db' on disk, instantiates Tk() GUI widgets, "
                    "and blocks in root.mainloop() on import."
                ),
                "explanation_of_mismatch": (
                    "Original script coupled SQLite disk connection and Tkinter UI creation directly at root module level "
                    "without an if __name__ == '__main__' guard, causing tests and headless imports to crash or hang."
                ),
            },
            "post_fix_runner_results": {
                "native_test_command": actual_cmd,
                "nonzero_test_count": test_count,
                "test_suite_status": "ALL_TESTS_PASSED",
                "oracle_comparison_count": len(oracle_comparisons),
                "oracle_comparisons": oracle_comparisons,
                "direct_assertions": direct_assertions,
            },
        }
        save_artifact("expected_vs_actual.json", expected_vs_actual)

        print("\n=======================================================")
        print(" ALL CHECKS PASSED SUCCESSFULLY")
        print(f" Native Command: {actual_cmd}")
        print(f" Nonzero Test Count: {test_count}")
        print(f" Oracle Inputs Evaluated: {len(oracle_comparisons)}")
        print(f" Artifacts saved in: {WORK_DIR}")
        print("=======================================================\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n[RUNNER ERROR] Check failed: {e}", file=sys.stderr)
        save_artifact("expected_vs_actual.json", {
            "status": "FAILED",
            "error": str(e),
        })
        sys.exit(1)


if __name__ == "__main__":
    main()
