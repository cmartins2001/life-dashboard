'''
Personal Life Dashboard with Streamlit
Last Updated: 7/8/2024
'''

# Libraries:
import pandas as pd
import streamlit as st
import gspread # for reading in Google sheets data
from oauth2client.service_account import ServiceAccountCredentials
import altair as alt

# Google API credentials:
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key_file_path = "C:/Users/cmart/Documents/daily_log_service_key_JSON.json"

# Function inputs:
google_sheet_name = "daily_log"
google_worksheet_name = "ParsedData"


# Function that connects to Google Sheets using a JSON key file path; returns the client variable:
def connect_to_sheets(json_path):
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    client = gspread.authorize(creds)
    return client


# Function that opens the google sheet and accesses a specific worksheet; returns values:
def open_sheet(client, sheet_name, worksheet_name):

    # Open the sheet:
    sheet = client.open(sheet_name)

    # Access the sheet of interest:
    my_worksheet = sheet.worksheet(worksheet_name)

    # Get values from sheet:
    data = my_worksheet.get_all_values()

    return data


# Function that converts values from Google Sheets into a pandas dataframe:
def create_df(sheets_data):
    return (pd.DataFrame(sheets_data[1:], columns=sheets_data[0]))


# Main function:
def main():
    # Connect:
    client_var = connect_to_sheets(json_key_file_path)

    # Get raw data:
    raw_data = open_sheet(client_var, google_sheet_name, google_worksheet_name)

    # Create a dataframe:
    google_df = create_df(raw_data)

    # Change the quantitative columns to float or int types:
    google_df['rating'] = pd.to_numeric(google_df['rating'], errors='coerce')
    google_df['rating'] = google_df['rating'].astype(float)
    google_df['hrs_outside'] = pd.to_numeric(google_df['hrs_outside'], errors='coerce')
    google_df['hrs_outside'] = google_df['hrs_outside'].fillna(0, inplace=False)

    # Print head:
    # print(google_df.head())

    ### START OF STREAMLIT EDITING ###

    # Create a title:
    st.title("Connor's Life Dashboard")

    # Create streamlit column layout:
    # col1, col2 = st.columns(2)

    # with col1:
        # Time series plot of daily rating:
    st.subheader("Daily Rating")
    # st.line_chart(data=google_df, x='date', y='rating')
    rating_line = alt.Chart(google_df).mark_line(color='deepskyblue').encode(
        x='date',
        y='rating'
    )
    st.altair_chart(rating_line)

    
    # with col2:
    # Bar chart of hours outside over time:
    st.subheader("Hours Spent Outside")
    # st.bar_chart(data=google_df, x='date', y='hrs_outside')
    outside_bar = alt.Chart(google_df).mark_bar(color='lightsalmon').encode(
        x='date',
        y='hrs_outside'
    )
    st.altair_chart(outside_bar)

    # Histogram of workouts by day of week:
    st.subheader("Workouts by Day of Week")
    # workout_hist = alt.Chart(google_df).mark_bar().encode(
    #     alt.X("date"),
    #     y='count()'
    # )
    ###NOTE: will probably need to create a count data frame using .agg() and then
    # do the histogram from there ###
    
    st.divider()

    # Raw data table:
    st.subheader("Raw Data")
    st.write(google_df)


if __name__ == "__main__":
    main()
