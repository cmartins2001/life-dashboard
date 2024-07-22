'''
Personal Life Dashboard with Streamlit
Last Updated: 7/22/2024
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


# Function that slices a dataframe based on an inputted date:
def date_slice_df(df, min_date):
    sliced_df = df[df['date'] >= min_date]
    return sliced_df


# Function that returns the mean of a column in a pandas dataframe:
def get_mean(df, col_name : str):
    return (df[col_name].mean())


# Function that generates a seven-day rolling average for a pandas DF column:
def seven_day_avg(df, col_name : str):

    # Retrieve the max date in the dataframe:
    max_date = df['date'].max()

    # Set the start date as 7 days before the max date:
    start_date = max_date - pd.offsets.Day(7)

    # Set the previous week's start date:
    last_wks_date = start_date - pd.offsets.Day(7)

    # Slice the dataframe for the most recent week:
    this_wks_df = df.loc[(df['date'] >= start_date) & (df['date'] <= max_date)]

    # Slice the dataframe for the previous week:
    last_wks_df = df.loc[(df['date'] >= last_wks_date) & (df['date'] <= start_date)]

    # Compute the two means:
    this_wks_mean = get_mean(this_wks_df, col_name)
    last_wks_mean = get_mean(last_wks_df, col_name)

    # Compute the percent change between the two averages:
    perc_change = ((this_wks_mean - last_wks_mean) / last_wks_mean) * 100

    # Return the 7-day average and the percent change relative to the previous week:
    return this_wks_mean, perc_change


# Main function:
def main():
    # Connect:
    client_var = connect_to_sheets(json_key_file_path)

    # Get raw data:
    raw_data = open_sheet(client_var, google_sheet_name, google_worksheet_name)

    # Create a dataframe:
    google_df = create_df(raw_data)

    # Change the quantitative columns to float or int types:

    # Rating:
    google_df['rating'] = pd.to_numeric(google_df['rating'], errors='coerce')
    google_df['rating'] = google_df['rating'].astype(float)

    # Hours outside:
    google_df['hrs_outside'] = pd.to_numeric(google_df['hrs_outside'], errors='coerce')
    google_df['hrs_outside'] = google_df['hrs_outside'].fillna(0, inplace=False)

    # Workout dummy:
    google_df['workout_bool'] = pd.to_numeric(google_df['workout_bool'], errors='coerce')
    google_df['workout_bool'] = google_df['workout_bool'].fillna(0, inplace=False)

    # Convert the date column to a pandas datetime variable:
    google_df['date'] = pd.to_datetime(google_df['date'], errors='coerce')

    # Check for any NaT values that were created due to parsing issues
    if google_df['date'].isna().sum() > 0:
        st.write(f"Warning: There are {google_df['date'].isna().sum()} invalid date entries that were converted to NaT")

    # Create a count dataframe for workouts by day of week visual:
    workout_df = google_df[['day_of_week', 'workout_bool']]
    workout_count_df = (workout_df
                        .groupby("day_of_week")
                        .agg({"workout_bool" : "sum"})
                        .reset_index()
                        .rename(columns={"workout_bool" : "workout_count"})
                        .sort_values(by='workout_count', ascending=False)
                        )

    ### START OF STREAMLIT EDITING ###

    # Create a title:
    st.title("Connor's :blue[Life] Dashboard")

    # Create streamlit column layout for KPIs:
    col1, col2 = st.columns(2)

    with col1:
        # st.metric('Average Daily Rating', f"{get_mean(google_df, 'rating'):.2f}")
        
        ### TESTING THE ROLLING AVERAGE FUNCTION BELOW ###
        st.metric('7-Day Average Rating', f"{seven_day_avg(google_df, 'rating')[0]:.2f}", f"{seven_day_avg(google_df, 'rating')[1]:.2f}%")

    with col2:
        # st.metric('Hours Outside Per Day', f"{get_mean(google_df, 'hrs_outside'):.2f}")
        st.metric('7-Day Average Rating', f"{seven_day_avg(google_df, 'hrs_outside')[0]:.2f}", f"{seven_day_avg(google_df, 'hrs_outside')[1]:.2f}%")
    
    
    # Time series plot of daily rating:
    st.subheader("Daily Rating")
    st.line_chart(data=google_df, x='date', y='rating')
    # rating_line = alt.Chart(google_df).mark_line(color='deepskyblue').encode(
    #     x='date',
    #     y='rating'
    # )
    # st.altair_chart(rating_line)

    
    # with col2:
    # Bar chart of hours outside over time:
    st.subheader("Hours Spent Outside")
    st.bar_chart(data=google_df, x='date', y='hrs_outside')
    # outside_bar = alt.Chart(google_df).mark_bar(color='lightsalmon').encode(
    #     x='date',
    #     y='hrs_outside'
    # )
    # st.altair_chart(outside_bar)

    # Histogram of workouts by day of week:
    st.subheader("Workouts by Day of Week")
    # workout_hist = alt.Chart(workout_count_df).mark_bar(color='forestgreen').encode(
    #     x='day_of_week',
    #     y='workout_count'
    # )
    # st.altair_chart(workout_hist)
    st.bar_chart(workout_count_df, x='day_of_week', y='workout_count')

    # Scatterplot of rating versus hours spent outside:
    st.subheader("Rating vs. Hours Outside")
    rating_outside_scatter = alt.Chart(google_df).mark_point().encode(
        x='hrs_outside',
        y='rating'
    )
    st.altair_chart(rating_outside_scatter)
    
    st.divider()

    # Raw data table:
    st.subheader("Raw Data")
    st.write(google_df)


if __name__ == "__main__":
    main()
