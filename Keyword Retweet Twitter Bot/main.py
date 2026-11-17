"""Keyword retweet bot contract.

Input: a search keyword, Twitter API credentials configured below, and an
existing writable ``bot.txt`` in the current working directory. The script
prints the authenticated account and retweet statuses, retweets up to 500
search results, and stores the number of successful retweets from this run in
``bot.txt``. It returns no value. Requires Tweepy and Twitter API access;
running it can retweet posts.
"""

import time

import tweepy

apic = ""  # add api_code
apisc = ""  # add api_secret_code

acc = ""  # add account_code
acsc = ""  # add account_secret_code


def main():
    auth = tweepy.OAuthHandler(apic, apisc)
    auth.set_access_token(acc, acsc)
    api = tweepy.API(
        auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
    )
    user = api.me()
    print(user.screen_name)
    search = input("Enter the keyword to be searched")
    count = 0

    with open("bot.txt", "r+") as counter_file:
        for tweet_number, tweet in enumerate(
            tweepy.Cursor(api.search, search).items(500)
        ):
            print("tweet-number", tweet_number, "retweeted")
            try:
                tweet.retweet()
            except tweepy.TweepError as error:
                print(error.reason)
                continue

            count += 1
            time.sleep(30)
            counter_file.seek(0)
            counter_file.write(str(count))
            counter_file.truncate()
            print("RETWEETED:", count)

        counter_file.seek(0)
        counter_file.write(str(count))
        counter_file.truncate()


if __name__ == "__main__":
    main()
