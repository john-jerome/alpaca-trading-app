import requests
import os
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

def next_market_open():

    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)

    next_open = response.json()['next_open']

    return next_open

def next_market_close():

    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
    
    response = requests.request('GET', url, headers=headers)

    next_close = response.json()['next_close']

    return next_close

def is_data_fresh(df, accepted_lag_mins):

    if df.empty:
        status = False
    else:
        end = df['window_end'][-1]
        print(end)
        status = True if end > generate_ts(-1*accepted_lag_mins) else False
        print(generate_ts(-1*accepted_lag_mins))
    return status

