import pandas as pd
import configparser
import requests
import sys
import json

sys.path.insert(0,'modules')

from database import Database
from telegramBot import send_message

config = configparser.ConfigParser()
config.read('config.ini')

class Portfolio:
    # database -> Database class
    def __init__(self, account_id):
        self.account_id = account_id
    
    def generate_auth_headers(self):
        
        if self.account_id == 'ua':
            headers = {
                'APCA-API-KEY-ID': 'PKXWA7LGA9LHVI6UT6RM',
                'APCA-API-SECRET-KEY': 'UpcoULBZm9XrW3u7sR5676TcjxZbzrOf1PKcd31v'
            }
        elif self.account_id == 'kz':
            headers = {
                'APCA-API-KEY-ID': 'PKXWA7LGA9LHVI6UT6RM',
                'APCA-API-SECRET-KEY': 'UpcoULBZm9XrW3u7sR5676TcjxZbzrOf1PKcd31v'
            }
        
        return headers

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
        # won't be used for now - add row selection later
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

        response = requests.request("POST", url, headers=self.generate_auth_headers(), data=payload)
        
        if response.status_code == 200:
            response_dict = response.json()
        
        return None

    def create_bracket_order(self, symbol, quantity, side, type, time_in_force, limit_price, stop_price, order_class = 'bracket'):
        url = "https://paper-api.alpaca.markets/v2/orders"

        payload = {}
        payload['symbol'] = symbol
        payload['qty'] = quantity
        payload['side'] = side
        payload['type'] = type
        payload['time_in_force'] = time_in_force
        payload['order_class'] = order_class
        payload['take_profit'] = {}
        payload['take_profit']['limit_price'] = limit_price
        payload['stop_loss'] = {}
        payload['stop_loss']['stop_price'] = stop_price

        response = requests.request("POST", url, headers=self.generate_auth_headers(), data=json.dumps(payload))
        print("Order status:", response.status_code)
        
        return None

    def get_current_portfolio(self):
        """[summary]

        Returns:
            [type]: [description]
        """

        url = "https://paper-api.alpaca.markets/v2/positions"

        response = requests.request("GET", url, headers=self.generate_auth_headers())

        if response.status_code == 200:
            positions = response.json()
        else:
            print("Couldn't get current portfolio.")

        return positions

    def is_in_potfolio(self, symbol):
        """Check if an instrument is already in the portfolio.

        Args:
            symbol (string): instrument symbol

        Returns:
            True or False
        """

        positions = self.get_current_portfolio()
        if symbol in [position['symbol'] for position in positions]:
            return True
        else:
            return False

    def get_open_orders(self, side):
        """[summary]

        Returns:
            [type]: [description]
        """

        url = "https://paper-api.alpaca.markets/v2/orders?status=open"
        payload = {}
        payload['status'] = 'closed'

        response = requests.request("GET", url, headers=self.generate_auth_headers(), params = json.dumps(payload))
        
        if response.status_code == 200:
            orders = response.json()
        else:
            print("Couldn't get open orders.")

        symbols = [order['symbol'] for order in orders if order['side'] == side]
        
        return list(set(symbols))
