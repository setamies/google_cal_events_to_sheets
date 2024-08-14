import datetime as dt
import os
import json
import pandas as pd

from constants import WORK_TAG
from typing import List
from app.api.calendar_api import get_google_api_data
from app.api.sheets_api import connect_to_sheets, push_data_to_sheets
from app.data_handling.data_processor import get_events_by_frequency, get_event_hours

def merge_and_replace_hours(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """    
    Args:
        df1 (pd.DataFrame): First DataFrame.
        df2 (pd.DataFrame): Second DataFrame.

    Returns:
        pd.DataFrame: Merged DataFrame with replaced 'hours worked' column.
    """
    # Convert 'date' columns to datetime if not already
    df1['date'] = pd.to_datetime(df1['date'], format='%d.%m.%Y')
    df2['date'] = pd.to_datetime(df2['date'])

    # Merge DataFrames using 'date' as the key, df2 data has priority
    merged_df = pd.merge(df1, df2, on='date', how='outer', suffixes=('_df1', '_df2'))
    merged_df['hours worked'] = merged_df['hours worked_df2'].combine_first(merged_df['hours worked_df1'])
    merged_df.drop(columns=['hours worked_df1', 'hours worked_df2'], inplace=True)
    return merged_df

def fetch_data(start_date: str, end_date: str) -> List[dict]:
    """
    Fetches data from the Google Calendar API, updates local JSON storage if new data is found,
    and returns a list of events.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        List[dict]: List of events in JSON format.
    """
    data = []
    file_path = 'data/events.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        last_stored_date = dt.datetime.strptime(data[-1]['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').date()
        start_date = (last_stored_date + dt.timedelta(days=1)).strftime('%Y-%m-%d')
        print(f'File exists, fetching data from {start_date}')
    else:
        start_date = dt.date(dt.date.today().year, 1, 1).strftime('%Y-%m-%d')

    new_data = get_google_api_data(start_date, end_date)

    if new_data:
        # Only update the file and data list if new data was actually fetched
        data.extend(new_data)
        with open(file_path, 'w') as file:
            json.dump(data, file)
    else:
        print("No new data found for the given date range.")

    return data

def main() -> None:
    """
    Main function to run the program.
    """
    print('Running main')
    today = dt.date.today()
    data = fetch_data(start_date=None, end_date=str(today))

    event_data = get_events_by_frequency(data, freq='daily')
    work_hours = get_event_hours(event_data, WORK_TAG)

    sheet_data = connect_to_sheets()
    sheet_update_df = merge_and_replace_hours(sheet_data, work_hours)
    push_data_to_sheets(sheet_update_df)

if __name__ == "__main__":
    main()
