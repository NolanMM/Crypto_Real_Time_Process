import praw
from datetime import datetime
import pandas as pd 
from time import sleep
import os
from dotenv import load_dotenv

SUBREDDITS = ["trading", "stockmarket", "investing", "stocks", "wallstreetbets"]
ALL_FIELDS = ["title", "url", "subreddit", "id", "created_utc", "news"]
FIELDS = ["title", "url", "subreddit", "id"]

load_dotenv(override=True)

client_id_ = os.getenv("REDDIT_CLIENT_ID")
client_secret_ = os.getenv("REDDIT_CLIENT_SECRET")
username_ = os.getenv("REDDIT_USER")
password_ = os.getenv("REDDIT_PASSWORD")
user_agent_ = os.getenv("REDDIT_USER_AGENT")


def init_reddit(reddit_client : str, reddit_secret : str):
    """Initialize the reddit instance"""
    return praw.Reddit(
        client_id=reddit_client,
        client_secret=reddit_secret,
        user_agent=user_agent_,
        username=username_,
        password=password_
    )

def reddit_stream(reddit):
    rows = []
    while True:
        recent_posts = reddit.subreddit("+".join(SUBREDDITS)).new(limit=100)
        for p in recent_posts:
            rows_dict = {field : str(getattr(p, field)) for field in FIELDS}
            rows_dict["created_utc"] = str(int(getattr(p, "created_utc") * 1000))
            rows.append(rows_dict)
        df = pd.DataFrame(rows)
        print(df)
        df.to_csv("reddit.csv", index=False)
        rows.clear()
        print(f"Finish write at {datetime.now()}")
        sleep(60)

def main():
    reddit = init_reddit(client_id_, client_secret_)
    reddit_stream(reddit)

if __name__ == "__main__":
    main()