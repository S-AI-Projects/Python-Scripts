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

target_directory = repository_root / "PNG To JPG"

try:
    import PIL
except ImportError:
    print("FAIL: Pillow is not installed.")
    sys.exit(1)

suite = unittest.defaultTestLoader.discover(
    start_dir=str(target_directory),
    pattern="test_*.py",
)

print("Running R35-T032 PNG To JPG boundary checks...")
result = unittest.TextTestRunner(verbosity=2).run(suite)
print("Tests executed: {}".format(result.testsRun))

if not result.wasSuccessful():
    sys.exit(1)
