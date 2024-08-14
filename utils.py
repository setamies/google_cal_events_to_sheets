import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def setup_google_client(api_name, api_version, scope, token_file, creds_file):
    """
    Set up Google client for specified API.

    Args:
        api_name (str): Name of the Google API (e.g., 'sheets', 'calendar').
        api_version (str): Version of the API (e.g., 'v4', 'v3').
        scope (list): Scopes needed for the API.
        token_file (str): File path to save the token.
        creds_file (str): File path to the client credentials.

    Returns:
        Google API service client.
    """
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scope)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scope)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build(api_name, api_version, credentials=creds)