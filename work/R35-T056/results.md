# R35-T056 check evidence

## Inputs used

- Credentials supplied to the fake bot: `EMAIL=student@example.com`, `PASSWORD=test-password` (test-only values; no real credentials).
- Tweet body expected from the target entry point: `My bot's first tweet!`.
- Failure case: the fake `post_tweets` raises `RuntimeError("posting failed")`.
- External I/O: mocked. The tests inject a fake `twitter_bot_class.TwitterBot` before executing `Twitter Selenium Bot/post_tweet.py`; Selenium, Firefox, webdriver-manager, and Twitter are not imported or contacted.

## Expected versus actual

| Check | Expected | Actual |
| --- | --- | --- |
| Successful run | Construct with the environment credentials, then `login`, post the fixed body, then `logout`; print nothing. | Exact expected sequence; no output. |
| Posting failure | Still call `logout` and print `posting failed` followed by a newline. | Exact expected sequence; output was `posting failed\n`. |
| Test count | At least one focused test; assertions must fail the runner. | 2 tests ran; both passed. Runner exited 0. |

## Command and test configuration

The repository has no discovered `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`, or `conftest.py` test configuration. The focused check therefore uses Python's standard-library `unittest` discovery on only `post_tweet_checks.py`:

- Required command: `python3 work/R35-T056/check.py`
- Command executed by the runner: `python3 -m unittest discover -s work/R35-T056 -p post_tweet_checks.py -v`
- Actual summary: `Ran 2 tests in 0.001s` — `OK`
- Test count is non-zero. `check.py` forwards a failing test's exit status and returns nonzero if discovery executes zero tests.

## Tool versions

- Python: 3.15.2
- Git: 2.50.1 (Apple Git-155)
- Platform: Darwin (macOS)
- Test framework: `unittest` from the Python standard library (Python 3.15.2)
