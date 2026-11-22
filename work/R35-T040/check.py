import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


repository_root = Path(__file__).resolve().parents[2]
target_directory = repository_root / "HTML to Images"
source_path = target_directory / "html-to-images.py"


def run_mutation_check():
    original_source = source_path.read_text(encoding="utf-8")
    original_line = "if len(background)>0:"
    mutated_line = "if len(background) >= 0:"

    if original_source.count(original_line) != 1:
        print("FAIL: expected one background condition to mutate")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        mutant_path = Path(temp_dir) / "html-to-images-mutant.py"
        mutant_path.write_text(
            original_source.replace(original_line, mutated_line, 1),
            encoding="utf-8",
        )

        environment = os.environ.copy()
        environment["HTML_TO_IMAGES_SCRIPT"] = str(mutant_path)
        command = [
            sys.executable,
            "-m",
            "unittest",
            "test_html_to_images.TestHtmlToImages."
            "test_smallest_html_with_empty_background_omits_css_argument",
        ]
        result = subprocess.run(
            command,
            cwd=str(target_directory),
            env=environment,
            capture_output=True,
            text=True,
        )

    combined_output = result.stdout + result.stderr
    expected_test_name = "test_smallest_html_with_empty_background_omits_css_argument"
    if (result.returncode == 0 or
            expected_test_name not in combined_output or
            "AssertionError" not in combined_output):
        print("FAIL: the empty-background assertion did not catch the mutant")
        print(combined_output)
        return False

    print("PASS: original passed; temporary one-line mutant failed the same empty-background assertion")
    return True


def main():
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(target_directory),
        pattern="test_*.py",
    )
    print("Running R35-T040 focused HTML-to-image tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("Original implementation tests executed: {}".format(result.testsRun))
    if not result.wasSuccessful():
        return 1

    if not run_mutation_check():
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
