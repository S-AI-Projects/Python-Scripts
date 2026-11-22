# R35-T037 Evidence

## Literal inputs

Source preconditions:

- `from_cel()` begins at `Convert Temperature/Convert Temperature.py` line 3.
- Line 22 reads the Celsius temperature as a float.
- Line 23 reads conversion choice `a` for Fahrenheit or `b` for Kelvin.
- Line 26 performs the Fahrenheit formula.
- Line 30 performs the Kelvin formula.

| Case | Literal input | Conversion choice | Independent calculation | Expected output |
|---|---|---|---|---|
| Smallest | `-273.15` Celsius | `b` (Kelvin) | `-273.15 + 273.15 = 0.0` | `The temperature is: 0.0 K` |
| Ordinary | `25` Celsius | `a` (Fahrenheit) | `25 * (9 / 5) = 45.0`; `45.0 + 32 = 77.0` | `The temperature is: 77.0 °F` |

## Expected versus actual

1. Smallest valid temperature:
   - Input: `-273.15`, then `b`
   - Expected intermediate: `0.0`
   - Expected output: `The temperature is: 0.0 K`
   - Actual output: `The temperature is: 0.0 K`
   - Result: PASS

2. Ordinary temperature:
   - Input: `25`, then `a`
   - Expected intermediate: `45.0`
   - Expected final: `77.0`
   - Expected output: `The temperature is: 77.0 °F`
   - Actual output: `The temperature is: 77.0 °F`
   - Result: PASS

3. Import safety:
   - Running the file under a non-`__main__` name must not call `input`.
   - Actual: no input call occurred.
   - Result: PASS

## Tool versions

- Python: 3.15.2
- Test framework: standard-library `unittest`
- No third-party dependencies are used.

## Actual test command

```text
python3 work/R35-T037/check.py
python3 -m doctest "Convert Temperature/Convert Temperature.py"
```

- Test count: 3
- Checker result: PASS
- Doctest result: PASS
