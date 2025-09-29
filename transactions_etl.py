'''load CSV files from copilot iOS budgeting app into duckdb database'''

import duckdb
import os
import pandas as pd
from datetime import datetime

# file drop and database location:
csv_dir = "C:/Users/cmart/databases/raw data"
db_path = "C:/Users/cmart/databases/connor_personal.duckdb"

# inputs:
table_nm = "transactions"
csv_file_path = os.path.join(csv_dir, "transactions.csv")
current_load_date = datetime.now().date().strftime('%Y-%m-%d')

# read and clean the CSV data:
df = (
    pd.read_csv(csv_file_path)

    # prep column names:
    .rename(columns=lambda x: x.strip().lower().replace(" ", "_"))

    # Data cleansing:
    .assign(
        date_name_amount_key=lambda x: x["date"].astype(str) + "-" + x["name"] + "-" + x["amount"].astype(str),
        date=lambda x: pd.to_datetime(x["date"]).dt.strftime('%Y-%m-%d'),
        name=lambda x: x["name"].fillna(""),
        amount=lambda x: x["amount"].fillna(0).astype(float),
        status=lambda x: x["status"].fillna(""),
        category=lambda x: x["category"].fillna(""),
        parent_category=lambda x: x["parent_category"].fillna(""),
        tags=lambda x: x["tags"].fillna(""),
        excluded=lambda x: x["excluded"].fillna(False).astype(bool),
        type=lambda x: x["type"].fillna(""),
        account=lambda x: x["account"].fillna(""),
        account_mask=lambda x: x["account_mask"].fillna(0).astype(int),
        note=lambda x: x["note"].fillna(""),
        recurring=lambda x: x["recurring"].fillna(""),
        recurring_bool=lambda x: x["recurring"].fillna("").apply(lambda y: True if y != "" else False),
        load_dt=current_load_date
    )

    # Deduplication and filtering:
    .drop(columns=["recurring"])
    .groupby(["date", "name", "amount", "status", "category", "parent_category", "excluded", "tags", "type", "account", "account_mask", "note", "date_name_amount_key", "recurring_bool", "load_dt"], as_index=False)
    .agg({"date_name_amount_key": "first"})  # deduplicate based on key
)

print(df.head(5))

# connect to DB
conn = duckdb.connect(db_path)

# Create table if it doesn't exist:
conn.execute(f'DROP TABLE IF EXISTS {table_nm};')
conn.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_nm} (
        date DATE,
        name TEXT,
        amount FLOAT,
        status TEXT,
        category TEXT,
        parent_category TEXT,
        excluded BOOL,
        tags TEXT,
        type TEXT,
        account TEXT,
        account_mask INTEGER,
        note TEXT,
        recurring BOOL, -- excluding for now
        load_dt DATE,
        date_name_amount_key TEXT PRIMARY KEY
    )
''')

conn.register("df_temp", df)
conn.execute(f'''
    INSERT INTO {table_nm}
    SELECT *
    FROM df_temp
    WHERE date_name_amount_key NOT IN (SELECT date_name_amount_key FROM {table_nm})
''')
conn.close()
