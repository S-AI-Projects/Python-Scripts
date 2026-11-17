import importlib.util
import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import call, patch


MAIN_PATH = Path(__file__).resolve().parents[1] / "main.py"


class FakeTweepError(Exception):
    @property
    def reason(self):
        return str(self)


class FakeTweet:
    def __init__(self, state, tweet_id, error=None):
        self.state = state
        self.tweet_id = tweet_id
        self.error = error

    def retweet(self):
        self.state["attempted"].append(self.tweet_id)
        if self.error:
            raise FakeTweepError(self.error)
        self.state["retweeted"].append(self.tweet_id)


class FakeAPI:
    def me(self):
        return types.SimpleNamespace(screen_name="fixture_user")

    def search(self, keyword):
        return None


class MemoryCounter(io.StringIO):
    def close(self):
        self.persisted_contents = self.getvalue()
        super().close()


class TestKeywordRetweetBot(unittest.TestCase):
    def setUp(self):
        self.state = {
            "attempted": [],
            "retweeted": [],
            "searched_keyword": None,
            "search_limit": None,
            "tweets": [],
        }

        fake_tweepy = types.ModuleType("tweepy")
        fake_tweepy.TweepError = FakeTweepError
        fake_tweepy.OAuthHandler = lambda *args: types.SimpleNamespace(
            set_access_token=lambda *tokens: None
        )
        fake_tweepy.API = lambda *args, **kwargs: FakeAPI()

        def fake_cursor(search, keyword):
            self.state["searched_keyword"] = keyword

            class Cursor:
                def items(inner_self, limit):
                    self.state["search_limit"] = limit
                    return iter(self.state["tweets"])

            return Cursor()

        fake_tweepy.Cursor = fake_cursor
        with patch.dict(sys.modules, {"tweepy": fake_tweepy}):
            spec = importlib.util.spec_from_file_location(
                "keyword_retweet_bot_main", MAIN_PATH
            )
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)

    def run_bot(self, keyword, tweets):
        self.state["tweets"] = tweets
        self.counter_file = MemoryCounter("")
        output = io.StringIO()

        def fake_open(path, mode):
            self.assertEqual(path, "bot.txt")
            self.assertEqual(mode, "r+")
            return self.counter_file

        with patch("builtins.input", return_value=keyword), patch(
            "builtins.open", side_effect=fake_open
        ), patch.object(self.module.time, "sleep") as sleep, redirect_stdout(
            output
        ):
            result = self.module.main()

        return {
            "return": result,
            "keyword": self.state["searched_keyword"],
            "limit": self.state["search_limit"],
            "attempted": self.state["attempted"],
            "retweeted": self.state["retweeted"],
            "sleep_calls": [entry.args[0] for entry in sleep.call_args_list],
            "counter": self.counter_file.persisted_contents,
            "output": output.getvalue().splitlines(),
        }

    def assert_results(self, expected, actual):
        self.assertEqual(
            actual,
            expected,
            f"Expected result: {expected!r}\nActual result: {actual!r}",
        )

    def test_smallest_keyword_and_empty_search(self):
        """Preconditions: main.py:30 takes a keyword; lines 33-35 search it."""
        expected = {
            "return": None,
            "keyword": "x",
            "limit": 500,
            "attempted": [],
            "retweeted": [],
            "sleep_calls": [],
            "counter": "0",
            "output": ["fixture_user"],
        }

        actual = self.run_bot("x", [])

        self.assert_results(expected, actual)

    def test_ordinary_keyword_and_single_retweet(self):
        """Preconditions: main.py:35 yields one result; lines 39, 44-49 retweet it."""
        tweets = [FakeTweet(self.state, 101)]
        expected = {
            "return": None,
            "keyword": "python",
            "limit": 500,
            "attempted": [101],
            "retweeted": [101],
            "sleep_calls": [30],
            "counter": "1",
            "output": [
                "fixture_user",
                "tweet-number 0 retweeted",
                "RETWEETED: 1",
            ],
        }

        actual = self.run_bot("python", tweets)

        self.assert_results(expected, actual)

    def test_repeated_successes_crossing_digit_boundary(self):
        """Preconditions: main.py:44 increments each success; lines 46-48 rewrite."""
        tweet_ids = [301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311]
        tweets = [FakeTweet(self.state, tweet_id) for tweet_id in tweet_ids]
        expected = {
            "return": None,
            "keyword": "python",
            "limit": 500,
            "attempted": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311],
            "retweeted": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311],
            "sleep_calls": [30] * 11,
            "counter": "11",
            "output": [
                "fixture_user",
                "tweet-number 0 retweeted",
                "RETWEETED: 1",
                "tweet-number 1 retweeted",
                "RETWEETED: 2",
                "tweet-number 2 retweeted",
                "RETWEETED: 3",
                "tweet-number 3 retweeted",
                "RETWEETED: 4",
                "tweet-number 4 retweeted",
                "RETWEETED: 5",
                "tweet-number 5 retweeted",
                "RETWEETED: 6",
                "tweet-number 6 retweeted",
                "RETWEETED: 7",
                "tweet-number 7 retweeted",
                "RETWEETED: 8",
                "tweet-number 8 retweeted",
                "RETWEETED: 9",
                "tweet-number 9 retweeted",
                "RETWEETED: 10",
                "tweet-number 10 retweeted",
                "RETWEETED: 11",
            ],
        }

        actual = self.run_bot("python", tweets)

        self.assert_results(expected, actual)

    def test_failed_retweet_is_reported_but_not_counted(self):
        """Preconditions: main.py:39 may fail; lines 40-42 report and continue."""
        tweets = [
            FakeTweet(self.state, 201, error="not permitted"),
            FakeTweet(self.state, 202),
        ]
        expected = {
            "return": None,
            "keyword": "python",
            "limit": 500,
            "attempted": [201, 202],
            "retweeted": [202],
            "sleep_calls": [30],
            "counter": "1",
            "output": [
                "fixture_user",
                "tweet-number 0 retweeted",
                "not permitted",
                "tweet-number 1 retweeted",
                "RETWEETED: 1",
            ],
        }

        actual = self.run_bot("python", tweets)

        self.assert_results(expected, actual)


if __name__ == "__main__":
    unittest.main()
