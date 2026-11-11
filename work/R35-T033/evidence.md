# R35-T033 Evidence

## Student Details
- Name: Suraj kumar
- URN: E26B07F1007
- Task ID: R35-T033 (Issue #33)
- Repository: S-AI-Projects/Python-Scripts
- Assigned working branch: student/e26b07f1007/R35-T033

## Target Item
- Module: `Hardware Detector/hardware_detector.py`
- Target Class: `HardwareDetector`
- Source Anchor: `self.hardware_profile = {}` (Line 34)
- Preconditions established at: `Hardware Detector/hardware_detector.py` lines 12-32 (contract and representative example docstring)

## Independent Reference Oracle
The independent oracle calculates the expected hardware dictionary directly via float division (`/ 1073741824.0`) and rounding to 2 decimal places, independently of the class implementation:
```python
def independent_oracle_calculator(total_bytes, used_bytes, free_disk_bytes, cores, usage_pct):
    GIB = 1073741824.0
    return {
        'ram_total_gb': round(total_bytes / GIB, 2),
        'ram_used_gb': round(used_bytes / GIB, 2),
        'available_diskspace_gb': round(free_disk_bytes / GIB, 2),
        'cpu_cores': int(cores),
        'cpu_usage_percent': float(usage_pct),
    }
```

## Tool Versions
- Python: 3.15.2
- psutil: 7.2.2
- OS: macOS (Darwin)

## Verification Results
1. Initialization Anchor Check:
   - Evaluated `self.hardware_profile` immediately upon `HardwareDetector()` creation.
   - Result: `{}` (Empty dictionary, PASS)

2. Smallest Valid Input:
   - System with 1 GB total RAM, 0 used, 1 GB disk free, 1 CPU core, 0.0% CPU usage.
   - Expected: `{'ram_total_gb': 1.0, 'ram_used_gb': 0.0, 'available_diskspace_gb': 1.0, 'cpu_cores': 1, 'cpu_usage_percent': 0.0}`
   - Actual: `{'ram_total_gb': 1.0, 'ram_used_gb': 0.0, 'available_diskspace_gb': 1.0, 'cpu_cores': 1, 'cpu_usage_percent': 0.0}`
   - Result: PASS

3. Ordinary Valid Input:
   - System with 16 GB total RAM, 8 GB used, 100 GB disk free, 8 cores, 15.5% CPU usage.
   - Expected: `{'ram_total_gb': 16.0, 'ram_used_gb': 8.0, 'available_diskspace_gb': 100.0, 'cpu_cores': 8, 'cpu_usage_percent': 15.5}`
   - Actual: `{'ram_total_gb': 16.0, 'ram_used_gb': 8.0, 'available_diskspace_gb': 100.0, 'cpu_cores': 8, 'cpu_usage_percent': 15.5}`
   - Result: PASS

4. Oracle Comparison across 25 Configurations:
   - 25 distinct synthetic system profiles evaluated against the independent oracle.
   - 25 / 25 matches (100% agreement).
   - Result: PASS

5. Deliberate Failure Proof:
   - Command: `FORCE_WRONG=1 python3 work/R35-T033/check.py`
   - Output: `FAIL: Expected {'ram_total_gb': 99.0...}, got {'ram_total_gb': 1.0...}`
   - Exit code: 1
