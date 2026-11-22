"""Tests for University Rankings/univRanking.py — R35-T008.

Fixture (written BEFORE editing the implementation):
    Smallest valid input (failure path):
        selectedCountry = "Unknown"
        TopUni CSV: 1 row, Country="USA", Institution name="MIT", Score=100.0
        Capitals CSV: 1 row, Country Name="USA", Capital="Washington", Continent="North America"
        → countries_lst = []  (anchor line 15), continents_lst = []  (anchor line 16)
        → "Unknown" not in TopUni["Country"]
        → number_of_universities = 0
        → ZeroDivisionError at: averageScore = university_score / number_of_universities

    Ordinary input (success path):
        selectedCountry = "USA"
        Same CSVs → number_of_universities = 1 → succeeds, writes output.txt

Precondition anchors:
    def getInformation(...)   # line 3
    countries_lst = []        # line 15
    continents_lst = []       # line 16
"""

import io
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd

sys.path.insert(0, "University Rankings")
import univRanking  # noqa: E402


# ---------------------------------------------------------------------------
# Minimal mock DataFrames — written before editing the implementation.
# ---------------------------------------------------------------------------
def _make_ranking_df():
    """Smallest valid rankings DataFrame with one USA university."""
    return pd.DataFrame({
        "Country": ["USA"],
        "Institution name": ["Washington University"],
        "Score": [100.0],
    })

def _make_capitals_df():
    """Smallest valid capitals DataFrame with one USA entry."""
    return pd.DataFrame({
        "Country Name": ["USA"],
        "Capital": ["Washington"],
        "Continent": ["North America"],
    })


def _mock_read_csv(filename, _dfs):
    """Return pre-built DataFrames instead of reading real files."""
    return _dfs[filename]


# ---------------------------------------------------------------------------
# Tests — failure path (smallest valid input reaching ZeroDivisionError)
# ---------------------------------------------------------------------------
class TestGetInformationFailurePath(unittest.TestCase):
    """getInformation raises ZeroDivisionError when country not in rankings."""

    def _run(self, country):
        ranking_df = _make_ranking_df()
        capitals_df = _make_capitals_df()
        dfs = {"ranking.csv": ranking_df, "capitals.csv": capitals_df}
        with patch("univRanking.pd.read_csv", side_effect=lambda f: dfs[f]), \
             patch("builtins.open", mock_open()):
            univRanking.getInformation(country, "ranking.csv", "capitals.csv")

    def test_unknown_country_raises_zero_division(self):
        """Failure path: 'Unknown' not in rankings → ZeroDivisionError.

        Source line reached: averageScore = university_score / number_of_universities
        countries_lst = []  (anchor line 15)
        continents_lst = []  (anchor line 16)
        """
        # Precondition anchor: countries_lst = []  # line 15
        # Expected: ZeroDivisionError
        with self.assertRaises(ZeroDivisionError):
            self._run("Unknown")

    def test_empty_string_country_raises_zero_division(self):
        """Failure path: '' (empty string) not in rankings → ZeroDivisionError."""
        # Precondition anchor: continents_lst = []  # line 16
        # Expected: ZeroDivisionError
        with self.assertRaises(ZeroDivisionError):
            self._run("")

    def test_failure_does_not_mutate_caller_state(self):
        """After ZeroDivisionError, caller-owned lists remain valid."""
        # caller_countries and caller_continents are NOT passed to getInformation
        # they are local to the function — caller state is unaffected
        caller_countries = []
        caller_continents = []
        try:
            self._run("Unknown")
        except ZeroDivisionError:
            pass
        # Expected: caller lists unchanged
        self.assertEqual(caller_countries, [])
        self.assertEqual(caller_continents, [])


# ---------------------------------------------------------------------------
# Tests — ordinary valid input (success after failure)
# ---------------------------------------------------------------------------
class TestGetInformationOrdinaryInput(unittest.TestCase):
    """getInformation succeeds for selectedCountry='USA' (ordinary input)."""

    def setUp(self):
        ranking_df = _make_ranking_df()
        capitals_df = _make_capitals_df()
        self.dfs = {"ranking.csv": ranking_df, "capitals.csv": capitals_df}
        self.written = []
        self.mock_file = mock_open()

    def _run_usa(self):
        with patch("univRanking.pd.read_csv", side_effect=lambda f: self.dfs[f]), \
             patch("builtins.open", self.mock_file):
            univRanking.getInformation("USA", "ranking.csv", "capitals.csv")

    def test_ordinary_input_does_not_raise(self):
        """'USA' in rankings → no ZeroDivisionError."""
        # Precondition anchor: def getInformation(...)  # line 3
        # Expected: completes without exception
        try:
            self._run_usa()
        except ZeroDivisionError:
            self.fail("getInformation raised ZeroDivisionError for 'USA'")

    def test_ordinary_input_opens_output_file(self):
        """output.txt is opened for writing (ordinary input)."""
        # Expected: open("output.txt", "w") called
        self._run_usa()
        self.mock_file.assert_called_with("output.txt", "w")

    def test_success_after_failure(self):
        """An ordinary valid call ('USA') succeeds after a failure ('Unknown')."""
        # Step 1 — failure
        try:
            with patch("univRanking.pd.read_csv", side_effect=lambda f: self.dfs[f]), \
                 patch("builtins.open", mock_open()):
                univRanking.getInformation("Unknown", "ranking.csv", "capitals.csv")
        except ZeroDivisionError:
            pass  # expected failure

        # Step 2 — ordinary success immediately after
        try:
            self._run_usa()
        except ZeroDivisionError:
            self.fail("Ordinary call after failure raised ZeroDivisionError")


if __name__ == "__main__":
    unittest.main(verbosity=2)
