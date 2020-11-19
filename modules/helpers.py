import requests
import os
import pandas as pd
from pytz import timezone
from datetime import datetime, timedelta

def generate_ts(delay_minutes=0):
    """Generate current UTC timestamp."""

    current_ts = datetime.now() + timedelta(minutes=delay_minutes)

    return current_ts

def unix_to_ts(unix_date):
    """Conver unix date to timestamp."""

    ts = datetime.fromtimestamp(unix_date).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    return ts

def ts_to_unix(ts):
    """Convert timestamp to unix date."""

    unix_date = datetime.timestamp(ts)

    return unix_date

def is_market_open():
    
    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)

    status = response.json()['is_open']

    return status

def time_to_market_open():

    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)

    next_open = datetime.strptime(response.json()['next_open'], '%Y-%m-%d %H:%M:%S.%f')
    current_ts = timezone('Europe/Berlin').localize(generate_ts())
    
    return next_open - current_ts

def time_to_market_close():

    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)


    next_close = datetime.strptime(response.json()['next_close'], '%Y-%m-%d %H:%M:%S.%f')
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
