import time
import pandas as pd
import configparser
import sys
import math
import numpy as np

sys.path.insert(0,'modules')

from database import generate_ts, ts_to_unix, insert_one_row
from orders import create_order
from helpers import get_last_N_prices, get_all_isin
from portfolio import is_in_potfolio, is_open_buy_order

config = configparser.ConfigParser()
config.read('config.ini')
db = config['sqlite']['database']

# collecting data for analysis
isin_for_analysis = ['US58933Y1055', 'US00287Y1091']

def verify_orders():
    """Thread to verify execution of open buy/sell orders

    Args:

    Returns:
        None
    """

    while not stop_event.is_set(): 

        time.sleep(period)

    print("Stop verifying orders...")
    return None

def calculate_moving_average(db_conn, window_length, buffer_size, isin):
    """Calculates moving averages for the isin
    The function shall be called periodically from the same place 
    Args:
        db_conn (sqlite3.connect): database connection object
        window_length (int): moving average window length
        buffer_size (int): size of buffer storing moving averages
        isin (string): isin of a financial instrument
    Raises:
        ValueError: not enough data in the database for calculating moving averages
    Returns:
        means (np.array): moving averages for the isin
    """
    # persistent dictionary to hold mean values
    try:
        calculate_moving_average.means
    except:
        calculate_moving_average.means = {}
    
    df = get_last_N_prices(db_conn, isin, window_length)
    # if not enough data for moving average calculation or wrong timestamps
    if len(df.index) < window_length:
        raise ValueError("Not suitable data for moving average calculation")
    mean = df['ask_price'].mean()

    # block to save data for analytics in mean_analysis
    if isin in isin_for_analysis:
        latest_timestamp = df.iloc[0]['date']
        row = (
            isin,
            mean.item(),
            latest_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        )
        insert_one_row(db_conn, row, table = 'mean_analysis')
    # check if isin appears for the first time
    if isin in calculate_moving_average.means:
        # Check if means list is full
        assert (len(calculate_moving_average.means[isin]) <= buffer_size)
        # add incoming mean value
        calculate_moving_average.means[isin].append(mean)
        # remove oldest mean if we have overflow
        if len(calculate_moving_average.means[isin]) > buffer_size:
            calculate_moving_average.means[isin].pop(0)
    else: # append to the dataframe if isin appears first time
        calculate_moving_average.means[isin] = [mean]

    return np.asarray(calculate_moving_average.means[isin])

def buy_shares(db_conn, isin, buy_amount, minutes_valid):
    print("Executing an order... buy isin:", isin)
    # buy: number of shares based on moving average price, valid for 5 minutes
    try:
        latest_stock_price = get_last_N_prices(db_conn, isin, 1).iloc[0]['bid_price']
        n_shares = math.floor(buy_amount/latest_stock_price)
        create_order(db_conn, isin, "buy", n_shares, ts_to_unix(generate_ts(minutes_valid)), "market", limit_price = None, stop_price = None)
    except:
        print("Buying shares failed")

    return None

def buy_strategy_first_momentum(db_conn, window_length, lookback_len):
    # do calculations for all isin
    for isin in get_all_isin(db_conn):
        # ignore isin if there is already open buy
        status, _ = is_open_buy_order(db_conn, isin)
        if status or is_in_potfolio(db_conn, isin):
            continue
        try:
            means = calculate_moving_average(db_conn, window_length, lookback_len + 1, isin)
        # ignore isin if means are not calculated yet
        except ValueError:
            continue
        # wait until enough moving average values are calculated
        if means.size < lookback_len + 1:
            continue
        deltas_means = np.diff(means)
        # check if momentum is changing to positive direction
        if np.all(np.all(deltas_means[1:] > deltas_means[:-1])):
            print(deltas_means)
            buy_shares(db_conn, isin, buy_amount, minutes_valid = 5)
        
    return None

def buy_strategy_moving_average(db_conn, buy_amount, window_length, lookback_len, buy_threshold):
    # do calculations for all isin
    for isin in get_all_isin(db_conn):
        # ignore isin if there is already open buy
        status, _ = is_open_buy_order(db_conn, isin)
        if status or is_in_potfolio(db_conn, isin):
            continue
        try:
            means = calculate_moving_average(db_conn, window_length, lookback_len + 1, isin)
        # ignore isin if means are not calculated yet
        except ValueError:
            continue
        # wait until enough moving average values are calculated
        if means.size < lookback_len + 1:
            continue
        # check if momentum is changing to positive direction
        if means[-1] - means[0] >= buy_threshold*means[0]:
            buy_shares(db_conn, isin, buy_amount, minutes_valid = 5)
    
    return None