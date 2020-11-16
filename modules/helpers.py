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
