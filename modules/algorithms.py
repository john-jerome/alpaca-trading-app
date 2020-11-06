import datetime
import time
import pandas as pd
import configparser
import sys
import math
from queue import Queue
import numpy as np

sys.path.insert(0,'modules')

from database import create_connection, select_data, generate_ts, ts_to_unix, insert_one_row, close_connection
from orders import verify_order_execution, create_order, get_current_portfolio, delete_order
from helpers import is_standard_hours, is_otc_hours, get_last_N_prices, get_all_isin

config = configparser.ConfigParser()
config.read('config.ini')

db = config['sqlite']['database']

current_ts = generate_ts()

ts_check = config.getboolean('internal_params', 'ts_check')
ts_delay = int(config['internal_params']['ts_delay'])
percent_diff = config.getfloat('algo_params', 'percent_diff')
profit_margin = config.getfloat('algo_params', 'profit_margin')
buy_amount = config.getint('algo_params', 'buy_amount')
percent_to_frac = config.getfloat('conversion_params', 'percent_to_frac')
stop_loss_threshold = config.getfloat('algo_params', 'stop_loss_threshold')

# collecting data for analysis
isin_for_analysis = ['US58933Y1055', 'US00287Y1091']

def is_in_potfolio(db_conn, isin):
    """Check if an instrument is already in the portfolio.

    Args:
        db_conn (sqlite3.connect): database connection object
        isin (string): isin of an instrument

    Returns:
        True or False
    """

    df_portfolio = get_current_portfolio()
    if isin in df_portfolio['isin'].unique():
        return True
    else:
        return False

def is_open_buy_order(db_conn, isin):
    """Check if there is an open buy order for isin.

    Args:
        db_conn (sqlite3.connect): database connection object
        isin (string): isin of an instrument

    Returns:
        status (boolean): True or False
        df_open_buy (pandas df): df with open buy orders for this instrument
    """

    sql_select_open_buy = """SELECT uuid, isin, type, quantity FROM open_buy_orders where isin = '{}'""".format(isin)
    open_buy = select_data(db_conn, sql_select_open_buy)
    df_open_buy = pd.DataFrame(open_buy, columns = ['order_uuid', 'isin', 'type', 'quantity'])

    if isin in df_open_buy['isin'].unique():
        status =  True
    else:
        status =  False

    return status, df_open_buy

def is_open_sell_order(db_conn, isin):
    """Check if there is an open sell order for isin.

    Args:
        db_conn (sqlite3.connect): database connection object
        isin (string): isin of an instrument

    Returns:
        status (boolean): True or False
        df_open_sell (pandas df): df with open sell orders for this instrument
    """

    sql_select_open_sell = """SELECT uuid, isin, type, quantity FROM open_sell_orders where isin = '{}'""".format(isin)
    open_sell = select_data(db_conn, sql_select_open_sell)
    df_open_sell = pd.DataFrame(open_sell, columns = ['order_uuid', 'isin', 'type', 'quantity'])

    if isin in df_open_sell['isin'].unique():
        status =  True
    else:
        status =  False

    return status, df_open_sell

def verify_orders(stop_event, period):
    """Thread to verify execution of open buy/sell orders

    Args:
        stop_event (thread.Event): stop event for the thread
        period (int): periodicity of the thread, seconds

    Returns:
        None
    """

    db_conn = create_connection(db)

    with db_conn:
        while not stop_event.is_set(): 
            sql_select_open_sell = """SELECT uuid FROM open_sell_orders"""
            df_sell = select_data(db_conn, sql_select_open_sell)
            df_sell = [''.join(i) for i in df_sell]
            for order_uuid in df_sell:
                verify_order_execution(db_conn, order_uuid)

            sql_select_open_buy = """SELECT uuid FROM open_buy_orders"""
            df_buy = select_data(db_conn, sql_select_open_buy)
            df_buy = [''.join(i) for i in df_buy]
            for order_uuid in df_buy:
                verify_order_execution(db_conn, order_uuid)

            time.sleep(period)

    close_connection(db_conn)
    print("Stop verifying orders...")
    return None

def buy_strategy_moving_average(db_conn, window_length, lookback_len, isin_for_analysis = isin_for_analysis):
    """[summary]

    Args:
        db_conn (sqlite3.connect): database connection object
        window_length (int): moving average window length
        lookback_len (int): lookback length for calculating price change

    Raises:
        ValueError: [description]

    Returns:
        None
    """
    try:
        buy_strategy_moving_average.df_moving_average
    except: 
        buy_strategy_moving_average.df_moving_average = pd.DataFrame(columns=['isin', 'moving average'])
    for isin in get_all_isin(db_conn):

        # ignore isin if there is already open buy
        status, _ = is_open_buy_order(db_conn, isin)
        if status or is_in_potfolio(db_conn, isin):
            continue
         
        df = get_last_N_prices(db_conn, isin, window_length)
        if len(df.index) >= window_length:
            if ts_check:
                raise ValueError("Data in the database is outdated.")
            else:
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
                if isin in buy_strategy_moving_average.df_moving_average['isin'].unique():
                    # add incoming mean value
                    isin_row = buy_strategy_moving_average.df_moving_average.loc[buy_strategy_moving_average.df_moving_average['isin'] == isin]
                    # Check if moving average list is full
                    assert (len(isin_row['moving average'][0]) <= lookback_len)
                    isin_row['moving average'][0].append(mean)
                    if len(isin_row['moving average'][0]) > lookback_len:
                        isin_row['moving average'][0].pop(0)
                        # check difference between first and last values
                        
                        last_price = isin_row['moving average'][0][-1]
                        if (last_price - isin_row['moving average'][0][0] >= percent_to_frac*percent_diff*isin_row['moving average'][0][0]):
                            print("Executing an order... buy isin:", isin)
                            # buy: number of shares based on moving average price, valid for 5 minutes
                            
                            latest_stock_price = df.iloc[0]['bid_price']
                            n_shares = math.floor(buy_amount/latest_stock_price)
                            create_order(db_conn, isin, "buy", n_shares, ts_to_unix(generate_ts(5)), "market", limit_price = None, stop_price = None)
                else: # append to the dataframe if isin appears first time
                    init_isin = pd.DataFrame({'isin': isin, 'moving average': [[mean]]})
                    buy_strategy_moving_average.df_moving_average = buy_strategy_moving_average.df_moving_average.append(init_isin)
        else:
            continue # not enough data for calculations
    return None

def sell_strategy_limit(db_conn):
    """Open a sell order in none already exists.
    If exists and the current price is too low, manually 'convert' it to a market order.

    Args:
        db_conn (sqlite3.connect): database connection object

    Returns:
        None
    """

    df_portfolio = get_current_portfolio()

    for _, row in df_portfolio.iterrows():

        status, df_open_sell = is_open_sell_order(db_conn, row['isin'])

        buy_price = row['price']
        total_quantity = row['quantity']

        if not status:
            print("Executing an order... sell isin:", row['isin'])
            create_order(db_conn, row['isin'], "sell", total_quantity, ts_to_unix(generate_ts(100)), "limit", limit_price = profit_margin*buy_price, stop_price = None)
        
        elif status:
            df = get_last_N_prices(db_conn, row['isin'], 1)
            if len(df.index) < 1:
                continue
            
            # getting current(latest) price from 'prices'
            latest_price = df.iloc[0]['bid_price']
            print(latest_price, buy_price)
            if (1.0 - latest_price / buy_price) > stop_loss_threshold:
                for _, row1 in df_open_sell.iterrows():
                    if row1['type'] != 'market':
                        delete_order(db_conn, row1['order_uuid'])
                        create_order(db_conn, row1['isin'], "sell", row1['quantity'], ts_to_unix(generate_ts(5)), "market", limit_price = None, stop_price = None)
                 

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
    if len(df.index) < window_length or ts_check:
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

    def buy_strategy_moving_average_2(db_conn, window_length, lookback_len):
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
            if means[-1] - means[0] >= percent_to_frac*percent_diff*means[0]:
                buy_shares(db_conn, isin, buy_amount, minutes_valid = 5)
        
        return None