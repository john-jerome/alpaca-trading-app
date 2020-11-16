import threading
import time
import configparser
import sys

sys.path.insert(0,'modules')
from strategy import Strategy
from database import Database

class TradingBot():
    def __init__(self, database_uri, strategy, account, period):
        self.__stop_trading = threading.Event()
        self.strategy = strategy
        self.account = account
        self.database_uri = database_uri
        self.period = period
        self.stop_flag = False
    
    def start(self):
        while not self.stop_flag:
            print("Bot is started")
            for trade in self.strategy.get_symbols_to_trade():
                if trade['order_class'] == 'bracket':
                    n_shares = math.floor(buy_amount/trade['limit_price'])
                    print("Creating a bracket order...")
                    self.account.create_bracket_order(trade['symbol'], n_shares, trade['side'], trade['type'], trade['time_in_force'], trade['limit_price'], trade['stop_price'])
            time.sleep(self.period)

        print("Stop trading ...")
        return None
    
    def stop(self):
        self.stop_flag = True