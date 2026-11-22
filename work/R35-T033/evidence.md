# R35-T033 Evidence

## Previous PR #63

PR #63 was closed and proposed the same type of changes: an import guard,
optional NVML fallback, a class contract, tests, and evidence.
Those changes were not present locally. The current source still imported
`pynvml` directly and executed `hardware.monitor_resources()` at module import.

## Existing and corrected behavior

Already present:

- `HardwareDetector.__init__` created `hardware_profile = {}`.
- `get_computer_specs()` gathered the five requested values.
- RAM and disk values were divided by `1024 ** 3` and rounded to two decimals.

Corrected in this task:

- The module no longer starts continuous monitoring during import.
- Missing or unavailable NVML support now produces the existing `"None available"`
  GPU fallback instead of stopping a test/import.

The original public method names and dictionary keys remain unchanged.

## Literal inputs

The smallest valid input has one source precondition: `hardware_profile` starts
as `{}` at `Hardware Detector/hardware_detector.py` line 13. The five computer
values are written by lines 48-52.

| Case | RAM total | RAM used | Free disk | CPU cores | CPU usage |
|---|---:|---:|---:|---:|---:|
| Smallest | 1 GiB | 0 GiB | 1 GiB | 1 | 0.0% |
| Ordinary | 16 GiB | 8 GiB | 100 GiB | 8 | 15.5% |

## Expected versus actual

Smallest input:

- Literal expected dictionary:
  `{'ram_total_gb': 1.0, 'ram_used_gb': 0.0, 'available_diskspace_gb': 1.0, 'cpu_cores': 1, 'cpu_usage_percent': 0.0}`
- Actual: the same dictionary.
- Result: PASS

Ordinary input:

- Literal expected dictionary:
  `{'ram_total_gb': 16.0, 'ram_used_gb': 8.0, 'available_diskspace_gb': 100.0, 'cpu_cores': 8, 'cpu_usage_percent': 15.5}`
- Actual: the same dictionary.
- Result: PASS

The mutation test also confirmed the same dictionary object remains in place,
an existing GPU key remains, and key order is:
`gpu_name`, `ram_total_gb`, `ram_used_gb`, `available_diskspace_gb`,
`cpu_cores`, `cpu_usage_percent`.

## Independent reference

The oracle uses a literal reference formula:
`round(byte_count / (1024 ** 3), 2)`.
It does not call `HardwareDetector.get_computer_specs()`.
Twenty-five literal configurations were compared.

## Baseline result

Before implementation, the baseline test command failed during module import:
continuous monitoring called live NVML and raised
`pynvml.NVMLError_LibraryNotFound`.

## Tool versions

- Python: 3.15.2
- psutil: 7.2.2
- pynvml: 13.0.1
- nvidia-ml-py: 13.615.71

## Final verification

- Command: `python3 work/R35-T033/check.py`
- unittest test methods: 4
- synthetic configurations: 25
- total focused checks: 29
- Result: PASS
