import random
import statistics
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


repository_root = Path(__file__).resolve().parents[2]
target_directory = repository_root / "Rock Paper Scissor 2"


class CountingChoices(list):
    def __init__(self, values):
        super().__init__(values)
        self.comparisons = 0

    def __contains__(self, value):
        for choice in self:
            self.comparisons += 1
            if value == choice:
                return True
        return False


def run_operation_experiment(rps_module):
    rng = random.Random(42)
    examples = {
        4: ("rock", "rock"),
        5: ("spock", "spock"),
        8: ("scissors", "scissors"),
    }
    sizes = [4, 5, 8]
    operation_counts = {size: [] for size in sizes}

    for repetition in range(5):
        repetition_sizes = sizes.copy()
        rng.shuffle(repetition_sizes)
        for size in repetition_sizes:
            word, expected = examples[size]
            fresh_input = "".join(
                character.upper() if rng.randint(0, 1) else character
                for character in word
            )
            measured_choices = CountingChoices(rps_module.choices)
            with patch("builtins.input", return_value=fresh_input):
                with patch.object(rps_module, "choices", measured_choices):
                    actual = rps_module.get_user_choice()

            if actual != expected:
                raise AssertionError(
                    "Expected {!r} from {!r}, got {!r}".format(
                        expected, fresh_input, actual
                    )
                )

            # Model one unit per character lowercased and one per list entry checked.
            operation_count = len(fresh_input) + measured_choices.comparisons
            operation_counts[size].append(operation_count)

    print("Operation-count model (5 fresh inputs per valid length; seed=42):")
    for size in sizes:
        counts = operation_counts[size]
        print(
            "  length {}: counts={}, median={}, range={}..{}".format(
                size,
                counts,
                statistics.median(counts),
                min(counts),
                max(counts),
            )
        )


def main():
    sys.path.insert(0, str(target_directory))
    import rps

    suite = unittest.defaultTestLoader.discover(
        start_dir=str(target_directory),
        pattern="test_*.py",
    )
    print("Running R35-T039 focused tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("Tests executed: {}".format(result.testsRun))
    if not result.wasSuccessful():
        return 1

    try:
        run_operation_experiment(rps)
    except AssertionError as error:
        print("FAIL: {}".format(error))
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
