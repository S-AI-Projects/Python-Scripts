import os
from twitter_bot_class import TwitterBot

def run_twitter_bot():
    try:
        pj = TwitterBot(os.environ['EMAIL'], os.environ['PASSWORD'])
        pj.login()
        pj.post_tweets("My bot's first tweet!")
        pj.logout()
    except Exception as e:
        pj.logout()
        print(e)


if __name__ == "__main__":
    run_twitter_bot()

