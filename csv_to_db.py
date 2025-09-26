'''load CSV files into duckdb database'''

import duckdb
import os
import pandas as pd

csv_dir = "C:/Users/cmart/databases/raw data"
db_path = "C:/Users/cmart/databases/connor_personal.duckdb"

# inputs:
new_table_name = "transactions"
csv_file_path = os.path.join(csv_dir, "transactions.csv")


# read and clean the CSV data:
df = (
    pd.read_csv(csv_file_path)
    .assign(
        date_name_amount_key=lambda x: x["date"].astype(str) + "-" + x["name"] + "-" + x["amount"].astype(str),
        date=lambda x: pd.to_datetime(x["date"]),
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
    )
    .drop(columns=["recurring"])
    .groupby(["date", "name", "amount", "status", "category", "parent_category", "excluded", "tags", "type", "account", "account_mask", "note", "date_name_amount_key", "recurring_bool"], as_index=False)
    .agg({"date_name_amount_key": "first"})  # deduplicate based on key
)

print(df.head())

# connect to DB
conn = duckdb.connect(db_path)

# Create table if it doesn't exist:
conn.execute(f'DROP TABLE IF EXISTS {new_table_name};')
conn.execute(f'''
    CREATE TABLE {new_table_name} (
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
        recurring BOOL,
        date_name_amount_key TEXT PRIMARY KEY
    )
''')
conn.register("df_temp", df)
conn.execute(f"INSERT INTO {new_table_name} SELECT * FROM df_temp;")
conn.close()
