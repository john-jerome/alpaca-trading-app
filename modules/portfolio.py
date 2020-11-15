import pandas as pd
import configparser
import requests
from Database import create_connection
config = configparser.ConfigParser()
config.read('config.ini')

class Portfolio:
    # database -> Database class
    def __init__(self, account_id, database_uri):
        self.account_id = account_id
        self.database_uri = database_uri
    def start(self):
        create_
    def create_simple_order(self, symbol, quantity, side, type, time_in_force, limit_price = None, stop_price = None):
        """[summary]

        Args:
            symbol ([type]): [description]
            quantity ([type]): [description]
            side ([type]): [description]
            type ([type]): [description]
            time_in_force ([type]): [description]
            limit_price ([type], optional): [description]. Defaults to None.
            stop_price ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        #time in force: https://alpaca.markets/docs/trading-on-alpaca/orders/#time-in-force
        url = "https://paper-api.alpaca.markets/v2/orders"

        payload = {}
        payload['symbol'] = symbol
        payload['qty'] = quantity
        payload['side'] = side
        payload['type'] = type
        payload['time_in_force'] = time_in_force
        if limit_price is not None:
            payload['limit_price'] = limit_price
        if stop_price is not None:    
            payload['stop_price'] = stop_price

        response = requests.request("POST", url, headers=self.auth_headers, data=payload)
        
        if response.status_code == 200:

            response_dict = response.json()
            
            #insert_one_row(self.db_conn, row, table = 'alpaca.orders')
        
        return None

    def create_bracket_order(self, order_class, symbol, quantity, side, type, time_in_force, limit_price, stop_price):
        pass

    def get_current_portfolio(self):
        """[summary]

        Returns:
            [type]: [description]
        """

        url = "https://paper-api.alpaca.markets/v2/positions"

        response = requests.request("GET", url, headers=self.auth_headers)

        if response.status_code == 200:
            positions = response.json()
        else:
            print("Couldn't get current portfolio.")

        return positions
    
    def delete_order(order_uuid):
        pass

    def is_in_potfolio(isin):
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

    def is_open_order(self, conn, isin, side):

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