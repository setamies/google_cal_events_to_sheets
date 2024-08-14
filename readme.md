# Google API - Calendar Events to Google Sheets

This project automates the process of fetching event data from Google Calendar, processing it, and updating Google Sheets with the results. The tool is designed to work with specific tags related to work activities, which are predefined in the configuration.

## Features

- Fetches events from Google Calendar based on a specified date range.
- Processes event data to calculate the duration of tagged activities.
- Updates a Google Sheets document with the processed data.
- Handles both daily and weekly event frequency.

## Setup

1. Ensure you have the necessary credentials files (`token.json` and `credentials.json`) for Google Calendar and Sheets API access.
2. Install the required Python packages using `pip install -r requirements.txt`.:


## Usage

Run the `main.py` script to execute the data fetching, processing, and updating routine. The script automatically fetches new data, processes it, and updates the connected Google Sheet with the results.

## Configuration

Update `constants.py` to adjust the Google API scopes, spreadsheet ID, and event tags as needed.