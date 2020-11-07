import datetime
import time
import pandas as pd
import configparser
import sys

from sqlite3 import Error

sys.path.insert(0,'modules')

from database import select_data, generate_ts

config = configparser.ConfigParser()
config.read('config.ini')

def get_last_N_prices(db_conn, isin, N):
    """Create a df containing last N prices for a specific isin.

    Args:
        db_conn (sqlite3.Connection): sqlite db connection object
        isin (string): isin of a stock
        N (int): number of prices to query

    Returns:
        pandas DataFrame: resulting dataframe
    """
    
    sql_select_last_N = """SELECT * FROM prices
    WHERE isin = '{}'
    ORDER BY timestamp DESC 
    LIMIT {} ;""".format(isin, N)

    result = select_data(db_conn, sql_select_last_N)
    df = pd.DataFrame(result, columns = ['isin', 'bid_price', 'ask_price', 'spread', 'date'])
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    return df

def get_all_isin(db_conn):
    """Get isin values from the database

    Args:
        db_conn (sqlite3.Connection): sqlite db connection object

    Returns:
        pandas DataFrame: dataframe of isins to trade
    """
    # we need to add a rule which stocks to choose - currently choosing more or less at random
    sql_get_all_isin = """SELECT * FROM trading_list"""

    df = select_data(db_conn, sql_get_all_isin)
    # convert tuples to string
    df = [''.join(i) for i in df] 
    return df
    
def prices_cleanup(db_conn, min_back = 60):
    """Delete data from prices table older than min_back minutes.

    Args:
        db_conn (sqlite3.Connection): sqlite db connection object
        min_back (int): minutes back. Default is 60 minutes.
    """

    sql_query_delete = """delete from prices where timestamp < '{}' and isin not in ('US58933Y1055','US00287Y1091')""".format(generate_ts(-1 * min_back))
    
    c = db_conn.cursor()
    
    try:
        c.execute(sql_query_delete)
        db_conn.commit()
    except Error as e:
        print(e)
    
    return None