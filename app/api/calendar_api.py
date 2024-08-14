import datetime
import os.path
import pytz
import json
from utils import setup_google_client
from constants import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_google_api_data(start_date, end_date):
    """Fetches events from the Google Calendar API within the provided date range and stores them in a JSON file.
  
    Args:
        start_date (str): The start date in YYYY-MM-DD format.
        end_date (str): The end date in YYYY-MM-DD format.
  
    Returns:
        A list of events or None if no events found.
    """
    service = setup_google_client("calendar", "v3", SCOPES, TOKEN_FILE, CREDS_FILE)
    timezone = pytz.timezone('Europe/Helsinki')
    start_time = timezone.localize(datetime.datetime.strptime(start_date, '%Y-%m-%d')).isoformat()
    end_time = timezone.localize(datetime.datetime.strptime(end_date, '%Y-%m-%d')).isoformat()
    
    try:
        print(f"Fetching events from {start_date} to {end_date}")
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        
        if not events:
            print("No events found within the specified range.")
            return None
        
        # Store events in json
        with open(EVENTS_JSON_PATH, 'w') as f:
            json.dump(events, f)
        
        return events
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
