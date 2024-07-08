'''
Personal Life Dashboard with Streamlit
Last Updated: 7/8/2024
'''

# Libraries:
import pandas as pd
import streamlit as st
import gspread # for reading in Google sheets data
from oauth2client.service_account import ServiceAccountCredentials

# Connect using Google API credentials:
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("path_to_your_service_account.json", scope)
client = gspread.authorize(creds)
