import sys
import unittest
from pathlib import Path


repository_root = Path(__file__).resolve().parents[2]
target_directory = repository_root / "Star Pattern"

suite = unittest.defaultTestLoader.discover(
    start_dir=str(target_directory),
    pattern="test_*.py",
)

print("Running R35-T038 starPattern focused checks...")
result = unittest.TextTestRunner(verbosity=2).run(suite)
print("Tests executed: {}".format(result.testsRun))

if not result.wasSuccessful():
    sys.exit(1)
