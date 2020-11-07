import pandas as pd

sys.path.insert(0,'modules')
from database import select_data
from orders import get_current_portfolio

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