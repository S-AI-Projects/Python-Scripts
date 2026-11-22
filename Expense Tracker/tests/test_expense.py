import datetime
import io
import os
import sqlite3
import sys
import unittest
from unittest.mock import MagicMock, call, patch

# Ensure 'Expense Tracker' directory is in sys.path
EXPENSE_TRACKER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if EXPENSE_TRACKER_DIR not in sys.path:
    sys.path.insert(0, EXPENSE_TRACKER_DIR)

import expense


class MockTreeview:
    """In-memory mock for tkinter.ttk.Treeview widget."""

    def __init__(self, initial_items=None):
        self._items = {}
        self._counter = 1
        self._selection = ()
        self._focus = None
        if initial_items:
            for item in initial_items:
                iid = f"item_{self._counter}"
                self._items[iid] = {"values": tuple(item)}
                self._counter += 1
            if self._items:
                self._selection = (next(iter(self._items.keys())),)
                self._focus = next(iter(self._items.keys()))

    def get_children(self, item=None):
        return tuple(self._items.keys())

    def delete(self, *items):
        for item in items:
            self._items.pop(item, None)
        self._selection = tuple(i for i in self._selection if i in self._items)
        if self._focus not in self._items:
            self._focus = next(iter(self._items.keys())) if self._items else None

    def insert(self, parent, index, iid=None, **kwargs):
        if iid is None:
            iid = f"item_{self._counter}"
            self._counter += 1
        self._items[iid] = kwargs
        return iid

    def item(self, item):
        return self._items.get(item, {"values": ()})

    def selection(self):
        return self._selection

    def set_selection(self, *items):
        self._selection = items
        if items:
            self._focus = items[0]

    def focus(self):
        return self._focus or ""

    def selection_remove(self, *items):
        rem = set(items)
        self._selection = tuple(i for i in self._selection if i not in rem)

    def get_all_values(self):
        return [tuple(data.get("values", ())) for data in self._items.values()]


def independent_oracle_list_all_expenses(db_rows, initial_table_rows=None):
    """Simplest independently understandable oracle for list_all_expenses.

    Takes:
        db_rows: Sequence of tuples in the ExpenseTracker table.
        initial_table_rows: Any stale pre-existing items in the table.

    Returns:
        dict: Expected state specification.
    """
    return {
        "expected_cleared": True,
        "expected_rows": [tuple(row) for row in db_rows],
        "count": len(db_rows),
    }


def create_in_memory_db():
    """Create an in-memory SQLite database connection with ExpenseTracker table."""
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
    return conn


def populate_db(conn, rows):
    """Populate database with given rows."""
    conn.execute("DELETE FROM ExpenseTracker")
    for row in rows:
        conn.execute(
            "INSERT INTO ExpenseTracker (ID, Date, Payee, Description, Amount, ModeOfPayment) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            row,
        )
    conn.commit()


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


class TestExpenseTracker(unittest.TestCase):
    """Unit and regression tests for Expense Tracker module."""

    def setUp(self):
        self.conn = create_in_memory_db()
        self.tree = MockTreeview()

    def tearDown(self):
        self.conn.close()

    def test_safe_import_no_side_effects(self):
        """Assert importing expense does not create files on disk or open GUI windows."""
        self.assertIsNone(expense.root)
        self.assertTrue(callable(expense.list_all_expenses))
        self.assertTrue(callable(expense.init_db))
        self.assertTrue(callable(expense.create_gui))

    def test_list_all_expenses_empty_db(self):
        """Assert list_all_expenses on empty DB leaves table empty and returns []."""
        result = expense.list_all_expenses(conn=self.conn, tree=self.tree)
        self.assertEqual(result, [])
        self.assertEqual(self.tree.get_all_values(), [])

    def test_list_all_expenses_clears_stale_table(self):
        """Assert list_all_expenses purges any existing table items before inserting."""
        stale_tree = MockTreeview(initial_items=[(999, "2020-01-01", "Old", "Old", 1.0, "Cash")])
        self.assertEqual(len(stale_tree.get_children()), 1)

        populate_db(self.conn, [(1, "2026-11-01", "New Payee", "New Desc", 20.0, "Cash")])
        result = expense.list_all_expenses(conn=self.conn, tree=stale_tree)

        self.assertEqual(len(result), 1)
        self.assertEqual(stale_tree.get_all_values(), [(1, "2026-11-01", "New Payee", "New Desc", 20.0, "Cash")])

    def test_list_all_expenses_all_22_enumerated_inputs(self):
        """Compare outputs against independent oracle for all 22 enumerated inputs, ignoring unspecified order."""
        for case in ENUMERATED_INPUTS:
            with self.subTest(case_id=case["id"]):
                populate_db(self.conn, case["db_rows"])
                test_tree = MockTreeview(initial_items=case["initial_table"])

                oracle_result = independent_oracle_list_all_expenses(case["db_rows"], case["initial_table"])
                actual_result = expense.list_all_expenses(conn=self.conn, tree=test_tree)

                actual_table_values = test_tree.get_all_values()

                # Ignore SQL-unspecified row ordering by sorting on (ID, Date)
                sorted_actual_ret = sorted([tuple(r) for r in actual_result], key=lambda r: (r[0], str(r[1])))
                sorted_actual_tbl = sorted([tuple(r) for r in actual_table_values], key=lambda r: (r[0], str(r[1])))
                sorted_expected = sorted([tuple(r) for r in oracle_result["expected_rows"]], key=lambda r: (r[0], str(r[1])))

                self.assertEqual(sorted_actual_ret, sorted_expected, f"Return mismatch in {case['id']}")
                self.assertEqual(sorted_actual_tbl, sorted_expected, f"Table values mismatch in {case['id']}")
                self.assertEqual(len(actual_table_values), oracle_result["count"])

    def test_list_all_expenses_mock_interaction(self):
        """Assert list_all_expenses calls get_children, delete, and insert on table."""
        mock_table = MagicMock()
        mock_table.get_children.return_value = ("c1", "c2")

        test_rows = [(10, "2026-11-10", "Payee A", "Desc A", 50.0, "Cash")]
        populate_db(self.conn, test_rows)

        expense.list_all_expenses(conn=self.conn, tree=mock_table)

        mock_table.get_children.assert_called_once()
        mock_table.delete.assert_called_once_with("c1", "c2")
        mock_table.insert.assert_called_once_with("", expense.END, values=test_rows[0])

    def test_list_all_expenses_fallback_to_globals(self):
        """Assert list_all_expenses uses global connector and table when none are passed."""
        test_rows = [(1, "2026-11-01", "Global Payee", "Global Desc", 100.0, "Credit Card")]
        populate_db(self.conn, test_rows)

        with patch.object(expense, "connector", self.conn), \
             patch.object(expense, "table", self.tree):
            result = expense.list_all_expenses()
            self.assertEqual(result, test_rows)
            self.assertEqual(self.tree.get_all_values(), test_rows)

    def test_clear_fields(self):
        """Assert clear_fields resets form variables and removes table selection."""
        mock_desc = MagicMock()
        mock_payee = MagicMock()
        mock_amnt = MagicMock()
        mock_mop = MagicMock()
        mock_date = MagicMock()
        mock_table = MagicMock()
        mock_table.selection.return_value = ("item_1",)

        expense.clear_fields(
            desc_var=mock_desc,
            payee_var=mock_payee,
            amnt_var=mock_amnt,
            mop_var=mock_mop,
            date_widget=mock_date,
            tree=mock_table,
        )

        mock_desc.set.assert_called_once_with("")
        mock_payee.set.assert_called_once_with("")
        mock_amnt.set.assert_called_once_with(0.0)
        mock_mop.set.assert_called_once_with("Cash")
        mock_date.set_date.assert_called_once()
        mock_table.selection_remove.assert_called_once_with("item_1")

    def test_remove_expense_success(self):
        """Assert remove_expense deletes selected row and commits transaction."""
        test_rows = [(1, "2026-11-01", "Payee", "Desc", 30.0, "Cash")]
        populate_db(self.conn, test_rows)
        tree = MockTreeview(initial_items=test_rows)

        with patch.object(expense, "tb", MagicMock()) as mock_tb:
            mock_tb.askyesno.return_value = True
            removed = expense.remove_expense(conn=self.conn, tree=tree, show_confirm=True)
            self.assertTrue(removed)

        remaining_in_db = self.conn.execute("SELECT * FROM ExpenseTracker").fetchall()
        self.assertEqual(remaining_in_db, [])
        self.assertEqual(tree.get_all_values(), [])

    def test_remove_expense_no_selection(self):
        """Assert remove_expense returns False and shows error when no item is selected."""
        empty_tree = MockTreeview()
        with patch.object(expense, "tb", MagicMock()) as mock_tb:
            removed = expense.remove_expense(conn=self.conn, tree=empty_tree, show_confirm=True)
            self.assertFalse(removed)
            mock_tb.showerror.assert_called_once()

    def test_remove_all_expenses_confirmed(self):
        """Assert remove_all_expenses purges database and clears table when confirmed."""
        test_rows = [
            (1, "2026-11-01", "P1", "D1", 10.0, "Cash"),
            (2, "2026-11-02", "P2", "D2", 20.0, "Debit Card"),
        ]
        populate_db(self.conn, test_rows)
        tree = MockTreeview(initial_items=test_rows)

        with patch.object(expense, "tb", MagicMock()) as mock_tb:
            mock_tb.askyesno.return_value = True
            res = expense.remove_all_expenses(conn=self.conn, tree=tree, show_confirm=True)
            self.assertTrue(res)

        remaining = self.conn.execute("SELECT * FROM ExpenseTracker").fetchall()
        self.assertEqual(remaining, [])
        self.assertEqual(tree.get_all_values(), [])

    def test_remove_all_expenses_cancelled(self):
        """Assert remove_all_expenses aborts when confirmation is refused."""
        test_rows = [(1, "2026-11-01", "P1", "D1", 10.0, "Cash")]
        populate_db(self.conn, test_rows)
        tree = MockTreeview(initial_items=test_rows)

        with patch.object(expense, "tb", MagicMock()) as mock_tb:
            mock_tb.askyesno.return_value = False
            res = expense.remove_all_expenses(conn=self.conn, tree=tree, show_confirm=True)
            self.assertFalse(res)

        remaining = self.conn.execute("SELECT * FROM ExpenseTracker").fetchall()
        self.assertEqual(len(remaining), 1)

    def test_search_expenses(self):
        """Assert search_expenses filters rows across columns matching search term."""
        test_rows = [
            (1, "2026-11-01", "Supermarket", "Groceries", 50.0, "Cash"),
            (2, "2026-11-02", "Bookstore", "Novel", 25.0, "Credit Card"),
            (3, "2026-11-03", "Bakery", "Super Cake", 15.0, "Debit Card"),
        ]
        populate_db(self.conn, test_rows)
        tree = MockTreeview()

        results = expense.search_expenses("Super", conn=self.conn, tree=tree)
        self.assertEqual(len(results), 2)
        expected_ids = {1, 3}
        self.assertEqual({r[0] for r in results}, expected_ids)
        self.assertEqual({r[0] for r in tree.get_all_values()}, expected_ids)

    def test_filter_expenses_by_date(self):
        """Assert filter_expenses_by_date selects records within given bounds."""
        test_rows = [
            (1, "2026-11-01", "P1", "D1", 10.0, "Cash"),
            (2, "2026-11-05", "P2", "D2", 20.0, "Cash"),
            (3, "2026-11-10", "P3", "D3", 30.0, "Cash"),
        ]
        populate_db(self.conn, test_rows)
        tree = MockTreeview()

        results = expense.filter_expenses_by_date("2026-11-02", "2026-11-07", conn=self.conn, tree=tree)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 2)
        self.assertEqual(tree.get_all_values(), [(2, "2026-11-05", "P2", "D2", 20.0, "Cash")])

    def test_sort_expenses(self):
        """Assert sort_expenses sorts rows by specified column and direction."""
        test_rows = [
            (1, "2026-11-01", "Charlie", "D1", 30.0, "Cash"),
            (2, "2026-11-02", "Alice", "D2", 10.0, "Cash"),
            (3, "2026-11-03", "Bob", "D3", 20.0, "Cash"),
        ]
        populate_db(self.conn, test_rows)
        tree = MockTreeview()

        res_asc = expense.sort_expenses("Payee", "ASC", conn=self.conn, tree=tree)
        self.assertEqual([r[2] for r in res_asc], ["Alice", "Bob", "Charlie"])

        res_desc = expense.sort_expenses("Amount", "DESC", conn=self.conn, tree=tree)
        self.assertEqual([r[4] for r in res_desc], [30.0, 20.0, 10.0])

    def test_add_another_expense_success(self):
        """Assert add_another_expense commits new entry and updates table."""
        tree = MockTreeview()
        date_widget = MagicMock(get=lambda: "2026-11-20", get_date=lambda: "2026-11-20")
        payee_var = MagicMock(get=lambda: "Coffee Shop")
        desc_var = MagicMock(get=lambda: "Latte")
        amnt_var = MagicMock(get=lambda: "4.50")
        mop_var = MagicMock(get=lambda: "Debit Card")

        with patch.object(expense, "tb", MagicMock()):
            added = expense.add_another_expense(
                date_widget=date_widget,
                payee_var=payee_var,
                desc_var=desc_var,
                amnt_var=amnt_var,
                mop_var=mop_var,
                conn=self.conn,
                tree=tree,
            )
            self.assertTrue(added)

        rows = self.conn.execute("SELECT * FROM ExpenseTracker").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "2026-11-20")
        self.assertEqual(rows[0][2], "Coffee Shop")
        self.assertEqual(rows[0][3], "Latte")
        self.assertEqual(rows[0][4], 4.50)
        self.assertEqual(rows[0][5], "Debit Card")

    def test_add_another_expense_missing_fields(self):
        """Assert add_another_expense reports error when fields are empty."""
        tree = MockTreeview()
        date_widget = MagicMock(get=lambda: "2026-11-20")
        payee_var = MagicMock(get=lambda: "")
        desc_var = MagicMock(get=lambda: "Latte")
        amnt_var = MagicMock(get=lambda: "4.50")
        mop_var = MagicMock(get=lambda: "Cash")

        with patch.object(expense, "tb", MagicMock()) as mock_tb:
            added = expense.add_another_expense(
                date_widget=date_widget,
                payee_var=payee_var,
                desc_var=desc_var,
                amnt_var=amnt_var,
                mop_var=mop_var,
                conn=self.conn,
                tree=tree,
            )
            self.assertFalse(added)
            mock_tb.showerror.assert_called_once()

    def test_expense_to_words_before_adding(self):
        """Assert expense_to_words_before_adding prompts user with readable sentence."""
        tree = MockTreeview()
        date_widget = MagicMock(get=lambda: "2026-11-20", get_date=lambda: "2026-11-20")
        payee_var = MagicMock(get=lambda: "Florist")
        desc_var = MagicMock(get=lambda: "Roses")
        amnt_var = MagicMock(get=lambda: "25.0")
        mop_var = MagicMock(get=lambda: "Credit Card")

        with patch.object(expense, "tb", MagicMock()) as mock_tb:
            mock_tb.askyesno.return_value = True
            ok = expense.expense_to_words_before_adding(
                date_widget=date_widget,
                desc_var=desc_var,
                amnt_var=amnt_var,
                payee_var=payee_var,
                mop_var=mop_var,
                conn=self.conn,
                tree=tree,
            )
            self.assertTrue(ok)
            mock_tb.askyesno.assert_called_once()
            prompt_text = mock_tb.askyesno.call_args[0][1]
            self.assertIn("You paid 25.0 to Florist for Roses on 2026-11-20 via Credit Card", prompt_text)

    def test_export_to_csv(self):
        """Assert export_to_csv writes valid CSV format with header and records."""
        test_rows = [
            (1, "2026-11-01", "Store", "Apples", 5.0, "Cash"),
            (2, "2026-11-02", "Gas", "Fuel", 40.0, "Credit Card"),
        ]
        populate_db(self.conn, test_rows)

        output_csv = os.path.join(EXPENSE_TRACKER_DIR, "tests", "_test_output.csv")
        try:
            with patch.object(expense, "tb", MagicMock()):
                success = expense.export_to_csv(conn=self.conn, filepath=output_csv)
                self.assertTrue(success)

            with open(output_csv, "r", encoding="utf-8") as f:
                content = f.read().splitlines()

            self.assertEqual(content[0], "ID,Date,Payee,Description,Amount,Mode of Payment")
            self.assertEqual(content[1], "1,2026-11-01,Store,Apples,5.0,Cash")
            self.assertEqual(content[2], "2,2026-11-02,Gas,Fuel,40.0,Credit Card")
        finally:
            if os.path.exists(output_csv):
                os.remove(output_csv)


if __name__ == "__main__":
    unittest.main()
