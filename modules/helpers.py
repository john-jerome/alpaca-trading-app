import requests
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
                'APCA-API-KEY-ID': 'PKXWA7LGA9LHVI6UT6RM',
                'APCA-API-SECRET-KEY': 'UpcoULBZm9XrW3u7sR5676TcjxZbzrOf1PKcd31v'
            }
    
    response = requests.request('GET', url, headers=headers)

    status = response.json()['is_open']

    return status