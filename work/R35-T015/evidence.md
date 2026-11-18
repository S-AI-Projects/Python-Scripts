# R35-T015 Evidence

## Student Details
- Name: Sangam
- URN: E26B07F0853
- Task ID: R35-T015 (Issue #15)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f0853/R35-T015

## Target Item
- Module: `Weather GUI/weather.py`
- Target function: `getWeather` and `parse_weather_data`
- Preconditions established at: `Weather GUI/weather.py`:
  - `requests` and `time` imports (lines 1-4)
  - `OPENWEATHER_BASE_URL` (line 8)
  - `parse_weather_data` (line 15)
  - `getWeather` (line 49)

## Repeatability & Isolation Strategy
- External HTTP networking dependency is decoupled and injected via `session` parameter (supporting mock session objects).
- JSON transformation logic is isolated in pure function `parse_weather_data`, eliminating UI and global state coupling.
- 100 consecutive executions verify zero state mutation, memory leakage, or drift across identical fixture inputs.

## Verification Results
1. Smallest valid input (minimal zero-offset JSON):
   - Input: minimal JSON (`temp: 273.15`, `sunrise: 21600`)
   - Expected Output: `"Clear\n0°C"`, `"\nMin Temp: 0°C..."`
   - Actual Output: Matches expected
   - Result: PASS

2. Ordinary valid input (London weather JSON):
   - Input: standard multi-field weather response
   - Expected Output: `"Clouds\n15°C"`, `"\nMin Temp: 12°C\nMax Temp: 17°C..."`
   - Actual Output: Matches expected
   - Result: PASS

3. Repeatability:
   - 100 consecutive runs evaluated
   - Identical output across all 100 runs
   - Result: PASS

4. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T015/check.py`
   - Output: `FAIL: Smallest input mismatch: expected 'WRONG_VALUE', got 'Clear\n0°C'`
   - Exit code: 1
