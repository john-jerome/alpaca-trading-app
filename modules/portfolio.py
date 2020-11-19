import pandas as pd
import requests
import sys
import json
import os

sys.path.insert(0,'modules')

from database import Database
from telegramBot import send_order_message

class Portfolio:
    # database -> Database class
    def __init__(self, account_id):
        self.account_id = account_id
    
    def generate_auth_headers(self):
        
        if self.account_id == 'ua':
            headers = {
                'APCA-API-KEY-ID': os.environ['APCA_API_KEY_ID'],
                'APCA-API-SECRET-KEY': os.environ['APCA_API_SECRET_KEY']
            }
        elif self.account_id == 'kz':
            headers = {
                'APCA-API-KEY-ID': '',
                'APCA-API-SECRET-KEY': ''
            }
        
        return headers

    def create_simple_order(
        self, symbol, quantity, side, 
        type, time_in_force, 
        limit_price = None, stop_price = None
        ):

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

        requests.request(
            "POST", url, 
            headers=self.generate_auth_headers(), data=payload
            )
        
        return None

    def create_bracket_order(
        self, symbol, quantity, side, 
        type, time_in_force, limit_price = None, 
        stop_price = None, order_class = 'bracket', 
        take_profit_limit_price = None,
        stop_loss_stop_price = None):

        url = "https://paper-api.alpaca.markets/v2/orders"

        payload = {}
        payload['symbol'] = symbol
        payload['qty'] = quantity
        payload['side'] = side
        payload['type'] = type
        payload['time_in_force'] = time_in_force

        if type in ['limit', 'stop_limit']:
            payload['limit_price'] = limit_price
        if type in ['stop', 'stop_limit']:
            payload['stop_price'] = stop_price

        payload['order_class'] = order_class

        # Additional parameters for bracket orders 
        payload['take_profit'] = {}
        payload['take_profit']['limit_price'] = take_profit_limit_price
        payload['stop_loss'] = {}
        payload['stop_loss']['stop_price'] = stop_loss_stop_price

        response = requests.request(
            "POST", url, headers=self.generate_auth_headers(), 
            data=json.dumps(payload)
            )

        status = response.status_code
        print("Order status:", status)

        if status == 200:
            send_order_message(
                self.account_id, action='create', 
                order_class='bracket', symbol=symbol, 
                order_type=type
                )
        
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

    def cancel_all_orders(self):

        url = "https://paper-api.alpaca.markets/v2/orders"

        response = requests.request("DELETE", url, headers=self.generate_auth_headers())
        
        print(response)
        

    def liquidate_all_positions(self):

        url = "https://paper-api.alpaca.markets/v2/positions"

        response = requests.request("DELETE", url, headers=self.generate_auth_headers())

        print(response)
