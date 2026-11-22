"""Behavioral checks for the Twitter Selenium Bot entry point.

The target module is executed with its TwitterBot import replaced by a fake so
these checks never construct a browser or make external requests.
"""

import contextlib
import io
import os
import runpy
import sys
import types
import unittest
from unittest.mock import patch


TARGET = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "Twitter Selenium Bot",
        "post_tweet.py",
    )
)


class FakeTwitterBot:
    def __init__(self, email, password, calls, failure=None):
        self.calls = calls
        self.failure = failure
        self.calls.append(("construct", email, password))

    def login(self):
        self.calls.append(("login",))
        if self.failure == "login":
            raise RuntimeError("login failed")

    def post_tweets(self, body):
        self.calls.append(("post_tweets", body))
        if self.failure == "post":
            raise RuntimeError("posting failed")

    def logout(self):
        self.calls.append(("logout",))


class PostTweetBehaviorChecks(unittest.TestCase):
    def execute_entry_point(self, failure=None):
        calls = []
        fake_module = types.ModuleType("twitter_bot_class")
        fake_module.TwitterBot = lambda email, password: FakeTwitterBot(
            email, password, calls, failure
        )
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"EMAIL": "student@example.com", "PASSWORD": "test-password"}),
            patch.dict(sys.modules, {"twitter_bot_class": fake_module}),
            contextlib.redirect_stdout(output),
        ):
            runpy.run_path(TARGET, run_name="__main__")
        return calls, output.getvalue()

    def test_posts_configured_tweet_in_order_and_returns_no_output(self):
        calls, output = self.execute_entry_point()

        self.assertEqual(
            calls,
            [
                ("construct", "student@example.com", "test-password"),
                ("login",),
                ("post_tweets", "My bot's first tweet!"),
                ("logout",),
            ],
        )
        self.assertEqual(output, "")

    def test_post_failure_still_logs_out_and_prints_exception(self):
        calls, output = self.execute_entry_point(failure="post")

        self.assertEqual(
            calls,
            [
                ("construct", "student@example.com", "test-password"),
                ("login",),
                ("post_tweets", "My bot's first tweet!"),
                ("logout",),
            ],
        )
        self.assertEqual(output, "posting failed\n")


if __name__ == "__main__":
    unittest.main()
