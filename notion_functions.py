'''
Creating a Streamlit dashboard that pulls data from a Notion Database
'''

import streamlit as st
from notion_client import Client
import pandas as pd


# Connect to Notion using the API key:
api_key = "secret_lmuB7awD6U51TPsK53bxAXWimn6CGJ0TgHsXnwIhN9R"
# Comment this out:
daily_log_id = "6193c636d6fb4e458316e565f0122e91"
notion = Client(auth=api_key)


# Function that returns a queried Notion DB using its ID:
def query_notion_db(db_id):
    return (notion.databases.query(database_id=db_id))


# Function that combines DB properties into a pandas dataframe:
def create_df():
    return ()

daily_log_query = query_notion_db(daily_log_id)
# for i in daily_log_query['results']:
#     print(i['properties'])

# Extract properties from Notion response (GPT):
data = []

for result in daily_log_query['results']:
    properties = result['properties']
    # Extract specific fields (adjust based on your Notion database structure)
    name = properties['Title']['title'][0]['text']['content'] if properties['Title']['title'] else None
    date = properties['date']['date']['start'] if properties['date']['date'] else None
    rating = properties['rating']['number'] if properties['rating']['number'] else None
    workout_bool = properties['workout_bool']['number'] if properties['workout_bool']['number'] else None
    hrs_outside = properties['hrs_outside']['number'] if properties['hrs_outside']['number'] else None
    weather = properties['weather']['rich_text'][0]['text']['content'] if properties['weather']['rich_text'] else None

    # Append extracted data to a list
    data.append({
        'name': name,
        'date': date,
        'rating': rating,
        'workout_bool': workout_bool,
        'hrs_outside': hrs_outside,
        'weather': weather
    })

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)
