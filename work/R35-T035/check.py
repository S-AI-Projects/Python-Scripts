import glob
import sys
import unittest
from pathlib import Path


repository_root = Path(__file__).resolve().parents[2]
venv_site_packages = list(
    glob.glob(str(repository_root / ".venv" / "lib" / "python*" / "site-packages"))
)
for path in venv_site_packages:
    sys.path.insert(0, path)

target_directory = repository_root / "JSON to CSV 2"

suite = unittest.defaultTestLoader.discover(
    start_dir=str(target_directory),
    pattern="test_*.py",
)

print("Running R35-T035 repeatability and isolation checks...")
result = unittest.TextTestRunner(verbosity=2).run(suite)
print("PASS/FAIL summary:")
print("  unittest test methods executed: {}".format(result.testsRun))

if not result.wasSuccessful():
    print("FAIL")
    sys.exit(1)

print("PASS")
