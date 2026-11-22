# Pre-refactor behavior record

Target: `Twitter Selenium Bot/post_tweet.py` (read before source changes).

## Public inputs and result

- It exposes no callable function and accepts no command-line arguments.
- When executed as a script, it reads `EMAIL` and `PASSWORD` from `os.environ` and uses the fixed message `My bot's first tweet!`.
- On normal completion, it has no structured result or explicit return value. The script exits normally and prints nothing.
- On an exception after `pj` has been assigned, it calls `pj.logout()` and prints the exception text. If that cleanup call itself fails, that cleanup exception propagates instead of printing the original one.

## Order, mutation, and external effects

Success call order is `TwitterBot(EMAIL, PASSWORD)`, `login()`, `post_tweets("My bot's first tweet!")`, `logout()`. The exception handler also attempts `logout()` before printing. Posting mutates the remote Twitter account by publishing a tweet; login/logout mutate the remote session, and the browser automation changes browser state. The target module itself does not write local files.

## Dependencies

- `os` (standard library) for environment-variable access.
- `TwitterBot` imported from sibling module `twitter_bot_class`.
- `twitter_bot_class` imports Selenium and `webdriver_manager`, creates a Firefox WebDriver at module import time, and uses the network/browser to interact with Twitter. Tests replace the `twitter_bot_class` module before loading the target, so neither that module nor external I/O is invoked.

## Baseline checks

`post_tweet_checks.py` exercises the entry point with mocked credentials and a fake `TwitterBot`. It records the successful call order and the failure cleanup/printed-error behavior. Baseline result before editing the target: 2 tests passed; command: `python3 -m unittest discover -s work/R35-T056 -p '*_checks.py' -v`.

## Extraction target

The smallest contiguous responsibility is the one-shot post workflow including its existing exception/cleanup handling. Give that workflow a clear function name, and leave the `__main__` guard to invoke it. Preserve its inputs (environment variables and existing fixed message), order, return behavior, and side effects.
