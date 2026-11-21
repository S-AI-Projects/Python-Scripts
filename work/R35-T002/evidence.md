# R35-T002 Evidence

## Student Details
- **Student Name**: Nitesh Kumar
- **URN**: e26b07f0629
- **Task ID**: R35-T002 (Issue #2)
- **Repository**: S-AI-Projects/Python-Scripts
- **Assigned working branch**: student/e26b07f0629/R35-T002

## Target Item
- **Module**: `Pizza Order/order.py`
- **Target Function**: `order_pizzas`, `main`
- **Source Fixture / Precondition Anchors**:
  - `pizza_lst = []` (order.py line 33): Master order list anchor.
  - `pizza_lst_current = []` (order.py line 34): Current transaction order list anchor.
  - `list_order_yes = ["Yes", "yes", "Y", "y", "YES"]` (order.py line 37): Affirmative order response domain.
  - `list_order_no = ["No", "no", "Q", "NO", "N", "n"]` (order.py line 38): Negative / exit order response domain.
  - `TOPPINGS` (order.py line 39): Supported 15-item toppings tuple domain.
  - `["S", "M", "L", "XL"]`: Supported size domain.

## Supported Boundary Table

| Boundary Aspect | Lower Boundary | Upper Boundary | Interior Values | Unsupported / Out-of-Domain Behavior | Source Line Reference |
|---|---|---|---|---|---|
| **Order Decision** | `"No"` / `"Q"` (declines order immediately, `pizza_lst = []`) | `"Yes"` (proceeds to size selection) | `"yes"`, `"y"`, `"YES"` | Strings not in `list_order_yes` or `list_order_no` are reprompted | `order.py:37-38, 48-50` |
| **Pizza Size** | `"S"` (Base price $7.99) | `"XL"` (Base price $13.99) | `"M"` ($9.99), `"L"` ($11.99) | Strings not in `["S", "M", "L", "XL"]` are reprompted | `order.py:42, 54-57` |
| **Topping Count** | `0` toppings (`"X"` immediately, no extra charge) | `3` toppings (included without extra fee) | `1`, `2` toppings | Extra fee applies starting at boundary `n = 4` toppings (> 3 toppings) | `order.py:39, 61-94` |
| **Extra Topping Fee Boundary** | Exactly `3` toppings ($0 extra charge) | Exactly `4` toppings (first fee threshold: 1 extra topping fee) | N/A | Calculated in `generateReceipt` ($0.50-$1.25/extra topping) | `pizzaReceipt.py:53-73` |
| **Control Sentinels** | `"LIST"`: Displays `TOPPINGS` without mutating list | `"X"`: Terminates toppings selection loop | N/A | Invalid toppings reprompted | `order.py:64-88` |

## Tool Versions
- **Python**: 3.15.0
- **Platform**: macOS (Darwin arm64)
- **Git Branch**: `student/e26b07f0629/R35-T002`

## Test Results and Evidence

### 1. Smallest Supported Input (Empty Order Boundary)
- **Literal Input**: `["No"]`
- **Precondition Anchor**: `pizza_lst = []` (line 33), `pizza_lst_current = []` (line 34)
- **Expected Return**: `[]`
- **Actual Return**: `[]`
- **Status**: PASS

### 2. Smallest Valid Pizza Order (Lower Size Boundary & 0 Toppings)
- **Literal Input**: `["Yes", "S", "X", "No"]`
- **Expected Return**: `[("S", [])]`
- **Actual Return**: `[("S", [])]`
- **Status**: PASS

### 3. Ordinary Valid Input
- **Literal Input**: `["Yes", "M", "PEPPERONI", "OLIVE", "X", "No"]`
- **Expected Return**: `[("M", ["PEPPERONI", "OLIVE"])]`
- **Actual Return**: `[("M", ["PEPPERONI", "OLIVE"])]`
- **Status**: PASS

### 4. Boundary Tests (One Test on Each Side of Documented Boundary)
- **3-Topping Boundary (No Extra Fee)**:
  - Input: `["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "X", "No"]`
  - Result: `[("S", ["ONION", "TOMATO", "MUSHROOM"])]` (len = 3) -> PASS
- **4-Topping Boundary (Incurs Extra Fee)**:
  - Input: `["Yes", "S", "ONION", "TOMATO", "MUSHROOM", "OLIVE", "X", "No"]`
  - Result: `[("S", ["ONION", "TOMATO", "MUSHROOM", "OLIVE"])]` (len = 4) -> PASS
- **Size Boundary (Upper Limit 'XL')**:
  - Input: `["Yes", "XL", "BACON", "X", "No"]`
  - Result: `[("XL", ["BACON"])]` -> PASS
- **Out-of-Domain Recovery Boundary**:
  - Reprompts invalid inputs (`'MAYBE'`, `'TINY'`, `'CHOCOLATE'`, `'PERHAPS'`) and cleanly recovers -> PASS
- **LIST Sentinel**:
  - Non-mutating display of `TOPPINGS` -> PASS

### 5. Native Test Runner Execution
- **Command**: `python3 -m unittest discover -s 'Pizza Order' -p 'test_*.py' -v`
- **Result**: Ran 9 tests in 0.001s — OK (0 failures, 0 errors)
- **Status**: PASS

### 6. Failure Propagation Proof
- **Command**: `FORCE_WRONG=1 python3 work/R35-T002/check.py`
- **Output**: `FAIL: Smallest valid empty order mismatch: expected [('WRONG', [])], got []`
- **Exit Code**: `1` (Non-zero exit on assertion failure verified)
- **Status**: PASS
