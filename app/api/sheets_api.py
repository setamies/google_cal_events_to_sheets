import os.path
import pandas as pd
from utils import setup_google_client
from constants import *

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def connect_to_sheets():
  service = setup_google_client("sheets", "v4", SHEETS_SCOPES, SHEETS_TOKEN_FILE, SHEETS_CREDS_FILE)
  try:
      # Call the Sheets API to fetch the data
      sheet = service.spreadsheets()
      result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
      values = result.get('values', [])

      if not values:
          print("No data found.")
          return None

      # Convert the data to a DataFrame
      df = pd.DataFrame(values[1:], columns=values[0])  # assuming first row is the header
      return df
  except Exception as e:
      print(f"An error occurred: {e}")
      return None
  
def push_data_to_sheets(df:pd.DataFrame):
    """
    Pushes data from a pandas DataFrame to a specific Google Sheet, handling credentials internally.
    The spreadsheet ID and range are predefined.

    Args:
        df (pd.DataFrame): DataFrame containing data to be pushed.
    """
    creds = None
    # Load or refresh existing credentials
    if os.path.exists("token_nethermind.json"):
        creds = Credentials.from_authorized_user_file("token_nethermind.json", SHEETS_SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            SHEETS_CREDS_FILE, SHEETS_SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open(SHEETS_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    if not creds or not creds.valid:
        print("Failed to establish credentials.")
        return

    try:
      # Check if there are datetime columns in the DataFrame, and turn them to strings
        for col in df.select_dtypes(include='datetime'):
            df[col] = df[col].dt.strftime('%d.%m.%Y')
        service = build("sheets", "v4", credentials=creds)
        values = [df.columns.tolist()] + df.values.tolist()  # Include headers
        body = {'values': values}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        print("Data successfully updated.")
    except HttpError as err:
        print(f"An error occurred: {err}")
