import praw
from datetime import datetime
import pandas as pd 
from time import sleep
import os
from dotenv import load_dotenv

SUBREDDITS = ["trading", "stockmarket", "investing", "stocks", "wallstreetbets"]
FIELDS = ["title", "url", "subreddit", "score", "num_comments", "ups", "id"]

load_dotenv(override=True)

client_id_ = os.getenv("REDDIT_CLIENT_ID")
client_secret_ = os.getenv("REDDIT_CLIENT_SECRET")
username_ = os.getenv("REDDIT_USER")
password_ = os.getenv("REDDIT_PASSWORD")
user_agent_ = os.getenv("REDDIT_USER_AGENT")

from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables from .env file
load_dotenv()

postgres_v = os.getenv("POSTGRES_VERSION")
postgres_url = os.getenv("POSTGRES_URL")
postgres_user = os.getenv("POSTGRES_USER")
postgres_pass = os.getenv("POSTGRES_PASSWORD")
postgres_table = os.getenv("POSTGRES_TABLE")
format_file = os.getenv("FORMAT_FILE")
_mode = os.getenv("MODE")
insert_query = os.getenv("INSERT_QUERY")
configure_table = os.getenv("CONFIGURE_TABLE")
create_table = os.getenv("CREATE_TABLE_QUERY")
connection_os_postgres = os.getenv("POSTGRE_CONNECTION")

def convert_unix_to_datetime(unix_timestamp):
    try:
        if isinstance(unix_timestamp, str):
            if unix_timestamp.isdigit():
                unix_timestamp = int(unix_timestamp)
            else:
                try:
                    datetime.strptime(unix_timestamp, '%Y-%m-%d %H:%M:%S')
                    return unix_timestamp
                except ValueError:
                    raise ValueError("Invalid Unix timestamp format")
        elif isinstance(unix_timestamp, int):
            pass
        else:
            raise ValueError("Invalid Unix timestamp format")
        
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error: {e}")
        return None

def init_postgresql(postgre_connection: str):
    connection = psycopg2.connect(postgre_connection)
    connection.set_client_encoding('UTF8')
    cursor = connection.cursor()
    cursor.execute(create_table)
    cursor.execute(configure_table)
    connection.commit()
    return connection, cursor

def write_to_postgresql(df, cursor, connection):
    """Write DataFrame to PostgreSQL database."""
    for _, row in df.iterrows():
        date_created_utc = convert_unix_to_datetime(row["date_created_utc"])
        
        if date_created_utc is None:
            print(f"Skipping row due to invalid timestamp: {date_created_utc}")
            continue
        row["date_created_utc"] = str(row["date_created_utc"])
        data = (row["id"], row["subreddit"], row["url"], row["title"].replace('\'', ""), row["score"], row["num_comments"], row["downvotes"], row["ups"], row["date_created_utc"])
        try:
            cursor.execute(insert_query, data)
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")
            continue


def init_reddit(reddit_client : str, reddit_secret : str):
    """Initialize the reddit instance"""
    return praw.Reddit(
        client_id=reddit_client,
        client_secret=reddit_secret,
        user_agent=user_agent_,
        username=username_,
        password=password_
    )

def reddit_stream(reddit, cursor_, connection_):
    """Stream the data from Reddit"""
    rows = []
    while True:
        recent_posts = reddit.subreddit("+".join(SUBREDDITS)).hot(limit=10)
        for p in recent_posts:
            rows_dict = {field : str(getattr(p, field)) for field in FIELDS}
            created_utc = str(int(getattr(p, "created_utc")))
            rows_dict["date_created_utc"] = str(datetime.fromtimestamp(int(created_utc)))
            rows_dict["downvotes"] = str(getattr(p, "ups") - getattr(p, "score"))
            rows.append(rows_dict)
        df = pd.DataFrame(rows)
        with open('reddit.csv', 'a', newline='', encoding='utf-8') as f:
            df.to_csv(f, header=f.tell()==0, index=False)
        if not df.empty:
            write_to_postgresql(df, cursor_, connection_)
        rows.clear()
        print(f"Finish write at {datetime.now()}")
        sleep(65)
        # print out the schema of recent_posts
        #print(recent_posts)

def main():
    reddit = init_reddit(client_id_, client_secret_)
    _connection, _cursor = init_postgresql(connection_os_postgres)
    reddit_stream(reddit, _cursor, _connection)

if __name__ == "__main__":
    main()