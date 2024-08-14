import pandas as pd
from datetime import datetime

def parse_events(events) -> pd.DataFrame:
    """Parses event data and converts datetime information."""
    parsed_data = [{
        'start': datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date'))),
        'end': datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date'))),
        'summary': event.get('summary', 'No Title Provided')
    } for event in events if 'dateTime' in event['start'] and 'dateTime' in event['end']]
    return pd.DataFrame(parsed_data)

def add_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add columns for year, month, week, and date, hours to a DataFrame."""
    df['start'] = pd.to_datetime(df['start'], utc=True)
    df['end'] = pd.to_datetime(df['end'], utc=True)

    df['duration'] = (df['end'] - df['start']).dt.total_seconds() / 3600.0
    df['year'] = df['start'].dt.year
    df['month'] = df['start'].dt.month
    df['week'] = df['start'].dt.isocalendar().week
    df['date'] = df['start'].dt.date
    return df

def get_events_by_frequency(events: pd.DataFrame, freq: str = 'W') -> pd.DataFrame:
    """Converts list of events to DataFrame, resamples by a given frequency,
    and sums durations for events with the same summary in each period."""
    if not events:
        return pd.DataFrame()  # Return empty DataFrame if no events
    df = parse_events(events)
    
    add_time_columns(df)    
    if freq == 'daily':
        return df.groupby(['date', 'summary'])['duration'].sum().reset_index()
    elif freq == 'weekly':
        return df.groupby(['year', 'week', 'summary'])['duration'].sum().reset_index()
    else:
        return pd.DataFrame()
    

def get_event_hours(df: pd.DataFrame, event_names: list, freq='daily') -> pd.DataFrame:
    """Returns the dataframe filtered by specified activities and aggregated by frequency."""
    if freq == 'daily':
        return df[df['summary'].isin(event_names)][['date', 'duration']].rename(columns={'duration': 'hours worked'})
    elif freq == 'weekly':
        return df[df['summary'].isin(event_names)][['year', 'week', 'duration']].rename(columns={'duration': 'hours worked'})

