import unittest
import sys
import os

# Ensure target directory is in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import pigeonhole as ph


class TestPigeonHoleSort(unittest.TestCase):
    """Failure-path and regression unit tests for pigeonhole_sort."""

    def test_fixture_permutations_and_duplicates(self):
        """
        Verify required fixtures:
        [3, 1, 2] -> [1, 2, 3]
        [2, 2, 1] -> [1, 2, 2]
        already ordered [1, 2, 3] -> [1, 2, 3]
        reversed [3, 2, 1] -> [1, 2, 3]
        """
        self.assertEqual(ph.pigeonhole_sort([3, 1, 2]), [1, 2, 3])
        self.assertEqual(ph.pigeonhole_sort([2, 2, 1]), [1, 2, 2])
        self.assertEqual(ph.pigeonhole_sort([1, 2, 3]), [1, 2, 3])
        self.assertEqual(ph.pigeonhole_sort([3, 2, 1]), [1, 2, 3])

    def test_smallest_supported_collection(self):
        """
        Smallest supported collections:
        - Single element: [42] -> [42]
        - Empty list: [] -> [] (absent-result branch)
        """
        self.assertEqual(ph.pigeonhole_sort([42]), [42])
        self.assertEqual(ph.pigeonhole_sort([]), [])

    def test_absent_result_branch_and_caller_state_isolation(self):
        """
        Exercise the absent-result branch with empty input and verify that
        caller-owned state remains valid and uncorrupted.
        """
        empty_input = []
        result = ph.pigeonhole_sort(empty_input)
        self.assertEqual(result, [])
        self.assertEqual(empty_input, [])

    def test_recovery_success_after_failure(self):
        """
        Verify an ordinary valid call succeeds immediately after exercising the empty branch.
        """
        # Call failure / absent-result branch
        ph.pigeonhole_sort([])

        # Ordinary valid call
        res = ph.pigeonhole_sort([8, 3, 2, 7, 4, 6, 8])
        self.assertEqual(res, [2, 3, 4, 6, 7, 8, 8])


if __name__ == "__main__":
    unittest.main()
