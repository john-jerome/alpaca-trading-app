import requests
import os
import pandas as pd
from pytz import timezone
from datetime import datetime, timedelta

def generate_ts(delay_minutes=0):
    """Generates current timestamp with an optional offset.

    Args:
        delay_minutes (int, optional): timestamp offset, in minutes. Defaults to 0.

    Returns:
        (datetime): Current timestamp.
    """
    current_ts = datetime.now() + timedelta(minutes=delay_minutes)

    return current_ts

def unix_to_ts(unix_date):
    """[summary]

    Args:
        unix_date ([type]): [description]

    Returns:
        [type]: [description]
    """

    ts = datetime.fromtimestamp(unix_date).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    return ts


def is_market_open():
    """Check if market is currently open.

    Returns:
        (boolean): True if open, False otherwise.
    """
    
    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)

    status = response.json()['is_open']

    return status

def time_to_market_open():
    """Calculates time in minutes till next market open.

    Returns:
        (int): Minutes till the next market open.
    """

    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)

    next_open = datetime.strptime(response.json()['next_open'], "%Y-%m-%dT%H:%M:%S%z")
    current_ts = timezone('Europe/Berlin').localize(generate_ts())
    diff = next_open - current_ts
    diff_minutes = int(diff.total_seconds() / 60.0)
    
    return diff_minutes

def time_to_market_close():

    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)


    next_close = datetime.strptime(response.json()['next_close'], "%Y-%m-%dT%H:%M:%S%z")
    current_ts = timezone('Europe/Berlin').localize(generate_ts())
    
    return next_close - current_ts

def is_data_valid(df, window_len):

    if len(df.index) < window_len:
        status = False
    else:
        accepted_lag = window_len + 3
        end = df['window_end'].iloc[-1]
        status = True if end > generate_ts(-1*accepted_lag) else False
    return status

print(type(generate_ts()))