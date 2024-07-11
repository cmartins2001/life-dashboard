'''
Personal Life Dashboard with Streamlit
Last Updated: 7/8/2024
'''

# Libraries:
import pandas as pd
import streamlit as st
import gspread # for reading in Google sheets data
from oauth2client.service_account import ServiceAccountCredentials

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

    # Change the rating column to a float type:
    google_df['rating'] = google_df['rating'].astype(float)

    # Print head:
    print(google_df.head())

    ### START OF STREAMLIT EDITING ###

    # Create a title:
    st.title("Connor's Life Dashboard")

    # Time series plot of daily rating:
    st.subheader("Daily Rating")
    # st.line_chart(google_df['rating'].astype(float))
    st.line_chart(data=google_df, x='date', y='rating')

    # Raw data table:
    st.subheader("Raw Data")
    st.write(google_df)


if __name__ == "__main__":
    main()
