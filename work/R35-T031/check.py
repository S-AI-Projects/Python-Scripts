import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TEST_DIRECTORY = REPOSITORY_ROOT / "Password Generator" / "tests"


suite = unittest.defaultTestLoader.discover(
    start_dir=str(TEST_DIRECTORY),
    pattern="test_*.py",
)
result = unittest.TextTestRunner(verbosity=2).run(suite)

print("Tests executed: {}".format(result.testsRun))

if not result.wasSuccessful():
    sys.exit(1)
