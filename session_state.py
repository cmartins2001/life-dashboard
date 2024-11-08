'''
testing out the session state feature of streamlit to improve user flow control
use this: https://docs.streamlit.io/develop/concepts/design/buttons
'''

import streamlit as st
import pandas as pd
import os

# globals:
repo_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script

# data:
raw = pd.read_csv("daily_log_example.csv")
raw = raw.loc[0:5, ]
# raw = raw.astype({'date':'category'})
test_names = ['raw', 'clicks']
test_vars = [raw, 0]

# functions
def initialize_session_state(names, vars):
    for name, variable in zip(names, vars):
        if name not in st.session_state:
            st.session_state[name] = variable


def click_button():
    st.session_state.clicks += 1


def reset_clicks():
    st.session_state.clicks = 0


def get_old_val_index(date_val) -> list:
    filtered_df = st.session_state.raw[st.session_state.raw['date'] == date_val]
    old_val_index = filtered_df.index
    return old_val_index#, old_val


def edit_data(new_val, row_index, col_name):
    st.session_state.raw.loc[row_index, col_name] = new_val


def reset_data():
    st.session_state.raw = pd.read_csv("daily_log_example.csv").loc[0:5, ]


# main w streamlit code:
def main():

    st.title("Session State Testing")

    # Set up the session state
    initialize_session_state(test_names, test_vars)

    # Display un-edited data:
    st.write("Original Data:")
    st.dataframe(raw)

    # Testing user input with multiple entries:
    # user_date = st.text_input("Enter edit date as a string:")
    # user_new_val = st.text_input("Enter the new value:")
    # user_new_val = int(user_new_val)
    # clicks = 0

    if st.button("Click to make edits"):
        user_date = st.text_input("Enter edit date as a string:")
        user_new_val = st.number_input("Enter the new value:")
        if st.button("Apply changes"):
            old_index = get_old_val_index(user_date)
            # click_button()
            st.session_state.clicks += 1
            edit_data(user_new_val, old_index, 'hrs_outside')
            st.dataframe(st.session_state.raw)

    st.write(f"Edit Count: {st.session_state.clicks}")

    if st.button("Reset data:", on_click=reset_clicks()):
        reset_data()
        st.dataframe(st.session_state.raw)

    # st.write(f"Edit Count: {st.session_state.clicks}")


if __name__ == '__main__':
    main()
