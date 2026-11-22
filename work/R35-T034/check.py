import glob
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


repository_root = Path(__file__).resolve().parents[2]
venv_site_packages = list(
    glob.glob(str(repository_root / ".venv" / "lib" / "python*" / "site-packages"))
)
for path in venv_site_packages:
    sys.path.insert(0, path)

try:
    from PIL import Image
except ImportError:
    print("FAIL: Pillow is not installed.")
    sys.exit(1)

target_directory = repository_root / "Wallpaper Changer"
suite = unittest.defaultTestLoader.discover(
    start_dir=str(target_directory),
    pattern="test_*.py",
)

print("Running R35-T034 add_margin invariant checks...")
result = unittest.TextTestRunner(verbosity=2).run(suite)
print("PASS/FAIL summary:")
print("  unittest test methods executed: {}".format(result.testsRun))
print("  deterministic seed: 42")
print("  generated valid cases: 100")

if not result.wasSuccessful():
    print("FAIL")
    sys.exit(1)

with tempfile.TemporaryDirectory() as temp_dir:
    temp_source = Path(temp_dir) / "broken_wallpaperchanger.py"
    shutil.copy2(target_directory / "wallpaperchanger.py", temp_source)
    text = temp_source.read_text()
    text = text.replace(
        "new_width = width + right + left",
        "new_width = width + left",
        1,
    )
    temp_source.write_text(text)

    spec = importlib.util.spec_from_file_location(
        "broken_wallpaperchanger", temp_source
    )
    broken_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(broken_module)

    original = Image.new("RGB", (1, 1), (100, 150, 200))
    broken = broken_module.add_margin(
        original, top=1, left=1, bottom=1, right=1, color=(0, 0, 0)
    )
    expected_broken_check_size = (3, 3)
    if broken.size == expected_broken_check_size:
        print("FAIL: deliberately broken copy did not break the size invariant")
        sys.exit(1)
    print("PASS: temporary broken copy changed size to {}, expected {} was detected".format(
        broken.size, expected_broken_check_size
    ))

print("PASS")
