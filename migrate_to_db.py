'''one-time script to migrate Notion database to duck DB database'''

import pandas as pd
from notion_client import Client
import duckdb
import os

repo_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(repo_dir, 'data')
local_data_dir = "C:/Users/cmart/databases"


# Connect to Notion using the API key:
api_key = "secret_lmuB7awD6U51TPsK53bxAXWimn6CGJ0TgHsXnwIhN9R"
notion = Client(auth=api_key)

# database IDs:
daily_log_id = "6193c636d6fb4e458316e565f0122e91"

def fetch_notion_data(db_id : str) -> pd.DataFrame:
    results = []
    has_more = True
    next_cursor = None
    while has_more:
        query = notion.databases.query(
            database_id=db_id,
            start_cursor=next_cursor
        )
        for page in query["results"]:
            props = page["properties"]

            # safely extract date:
            date_obj = props.get("date", {}).get("date", {})
            date_value = date_obj.get("start") if date_obj else None

            # safely extract weather:
            weather_obj = props.get("weather", {}).get("rich_text", [{}])
            if type(weather_obj) is not list or len(weather_obj) == 0:
                weather_value = None
            else:
                weather_value = weather_obj[0]["text"]["content"]

            # create a row of data to be added:
            row = {
                "id": page["id"],  # Notion page ID for uniqueness
                "date": date_value,
                "rating": props.get("rating", {}).get("number", 0),
                "workout_bool": props.get("workout_bool", {}).get("number", 0),
                "hrs_outside": props.get("hrs_outside", {}).get("number", 0),
                "weather": weather_value
                # "weather": props.get("weather", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            }
            results.append(row)
        next_cursor = query.get("next_cursor")
        has_more = query.get("has_more")
    return pd.DataFrame(results)


def main():

    # Fetch data from daily log database and clean columns:
    df = (
            fetch_notion_data(db_id=daily_log_id)
            .assign(
                date=lambda x: pd.to_datetime(x["date"]),
                rating=lambda x: x["rating"].fillna(0).astype(float),
                workout_bool=lambda x: x["workout_bool"].fillna(0).astype(int),
                hrs_outside=lambda x: x["hrs_outside"].fillna(0).astype(float),
                weather=lambda x: x["weather"].fillna(""),
            )
        )

    print(df.head())

    # Set-up / connect to duckdb:
    db_path = os.path.join(local_data_dir, 'connor_personal.duckdb')
    if not os.path.exists(local_data_dir):
        os.makedirs(local_data_dir)
    conn = duckdb.connect(db_path)

    # Create table if it doesn't exist:
    conn.execute('DROP TABLE IF EXISTS daily_log;')
    conn.execute('''
        CREATE TABLE daily_log (
            id TEXT PRIMARY KEY,
            date DATE,
            rating FLOAT,
            workout_bool INTEGER,
            hrs_outside FLOAT,
            weather TEXT
        )
    ''')

    conn.register("df_temp", df)
    conn.execute("INSERT INTO daily_log SELECT * FROM df_temp;")
    conn.close()


if __name__ == '__main__':
    main()
