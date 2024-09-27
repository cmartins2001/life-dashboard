'''
Creating a Streamlit dashboard that pulls data from a Notion Database
'''

import streamlit as st
from notion_client import Client
import pandas as pd
from dashboard import *


# Connect to Notion using the API key:
api_key = "secret_lmuB7awD6U51TPsK53bxAXWimn6CGJ0TgHsXnwIhN9R"
# Comment this out:
daily_log_id = "6193c636d6fb4e458316e565f0122e91"
notion = Client(auth=api_key)


# Function that returns a queried Notion DB using its ID:
def query_notion_db(db_id):
    return (notion.databases.query(database_id=db_id))


# Function that returns a dataframe from a query:
def create_df(query):

    # Initialize a list:
    data = []

    for result in query['results']:
        properties = result['properties']
        # Extract specific fields (adjust based on your Notion database structure)
        name = properties['Title']['title'][0]['text']['content'] if properties['Title']['title'] else None
        date = properties['date']['date']['start'] if properties['date']['date'] else None
        rating = properties['rating']['number'] if properties['rating']['number'] else None
        workout_bool = properties['workout_bool']['number'] if properties['workout_bool']['number'] else None
        hrs_outside = properties['hrs_outside']['number'] if properties['hrs_outside']['number'] else None
        weather = properties['weather']['rich_text'][0]['text']['content'] if properties['weather']['rich_text'] else None

        # Append extracted data to the list:
        data.append({
            'name': name,
            'date': date,
            'rating': rating,
            'workout_bool': workout_bool,
            'hrs_outside': hrs_outside,
            'weather': weather
        })

        return (pd.DataFrame(data))


def main():
    
    # Query the daily log database in Notion:
    daily_log_query = query_notion_db(daily_log_id)

    # Create a pandas dataframe from the query:
    daily_log_df = create_df(daily_log_query)

    # Print the type of the date column:
    # st.write(daily_log_df['date'].dtype)

    # Change the date column to datetime format:
    daily_log_df = daily_log_df.assign(
        date=pd.to_datetime(daily_log_df['date'].dt.strftime("%Y-%m"))
        )

    ### START OF STREAMLIT EDITING ###

    # Create a title:
    st.title("Connor's :blue[Life] Dashboard")

    # Create streamlit column layout for KPIs:
    col1, col2 = st.columns(2)

    with col1:
        # st.metric('Average Daily Rating', f"{get_mean(google_df, 'rating'):.2f}")
        
        ### TESTING THE ROLLING AVERAGE FUNCTION BELOW ###
        st.metric('7-Day Average Rating', f"{seven_day_avg(daily_log_df, 'rating')[0]:.2f}", f"{seven_day_avg(daily_log_df, 'rating')[1]:.2f}%")

    with col2:
        # st.metric('Hours Outside Per Day', f"{get_mean(google_df, 'hrs_outside'):.2f}")
        st.metric('7-Day Avg Hrs Outside', f"{seven_day_avg(daily_log_df, 'hrs_outside')[0]:.2f}", f"{seven_day_avg(daily_log_df, 'hrs_outside')[1]:.2f}%")

    # Time series plot of daily rating:
    st.subheader("Daily Rating")
    st.line_chart(data=daily_log_df, x='date', y='rating')



if __name__ == "__main__":
    main()
