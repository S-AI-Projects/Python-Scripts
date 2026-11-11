# R35-T037 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T037 (Issue #37)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T037

## Target Item
- Module: `Convert Temperature/Convert Temperature.py`
- Target Function: `from_cel(temp=None, target_unit=None)`
- Precondition lines: Lines 6-25 (Float validation, unit selector 'a'/'b', formula evaluation)

## Worked Examples and Decisive State Transitions
1. Smallest Physical Temperature (-273.15 °C to Kelvin):
   - Input: `temp = -273.15, target_unit = 'b'`
   - State transition: `final = -273.15 + 273.15 = 0.0`
   - Output string: `"The temperature is: 0.0 K"`
2. Ordinary Temperature (25.0 °C to Fahrenheit):
   - Input: `temp = 25.0, target_unit = 'a'`
   - State transition: `scaled = 25.0 * (9/5) = 45.0` -> `final = 45.0 + 32 = 77.0`
   - Output string: `"The temperature is: 77.0 °F"`

## Tool Versions
- Python: 3.15.2
- OS: macOS (Darwin)

## Verification Results
1. Smallest Valid Input Execution:
   - Evaluated `from_cel(-273.15, 'b')`
   - Value: `0.0`, Output: `"The temperature is: 0.0 K"`
   - Result: PASS

2. Ordinary Valid Input Execution:
   - Evaluated `from_cel(25.0, 'a')`
   - Value: `77.0`, Output: `"The temperature is: 77.0 °F"`
   - Result: PASS

3. Interactive Stdin Compatibility:
   - Evaluated `from_cel()` with mocked user inputs `["0.0", "a"]`
   - Value: `32.0`, Output: `"The temperature is: 32.0 °F"`
   - Result: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T037/check.py`
   - Output: `FAIL: Expected The temperature is: 999.0 K, got The temperature is: 0.0 K`
   - Exit code: 1
