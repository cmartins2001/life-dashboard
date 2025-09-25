'''one-time script to migrate Notion database to duck DB database'''

import pandas as pd
from notion_client import Client
import duckdb


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
            row = {
                "id": page["id"],  # Notion page ID for uniqueness
                "date": props.get("Date", {}).get("date", {}).get("start"),
                "mood": props.get("Mood (1-10)", {}).get("number", 0),
                "exercise": props.get("Exercise", {}).get("checkbox", False),
                # Add more properties here, e.g., "notes": props.get("Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            }
            results.append(row)
        next_cursor = query.get("next_cursor")
        has_more = query.get("has_more")
    return pd.DataFrame(results)


def main():

    # Fetch data from daily log database:
    df = fetch_notion_data(db_id=daily_log_id)
    df["date"] = pd.to_datetime(df["date"])  # Clean dates
    df["exercise"] = df["exercise"].astype(int)  # Convert bool to 0/1 for DB

    print(df.head())

    # Set-up / connect to duckdb:
    # conn = duckdb.connect('connor_personal.duckdb')

    # Create table if it doesn't exist:
    # conn.execute('''
    #     CREATE TABLE IF NOT EXISTS daily_log (
    #         id TEXT PRIMARY KEY,
    #         date DATE,
    #         mood INTEGER,
    #         exercise INTEGER
    #     )
    # ''')


if __name__ == '__main__':
    main()
