import threading
import time
import configparser
import sys
import math

sys.path.insert(0,'modules')

from strategy import Strategy
from database import Database
from portfolio import Portfolio

config = configparser.ConfigParser()
config.read('config.ini')

class TradingBot():
    def __init__(self, strategy, account, period):
        self.strategy = strategy
        self.account = account
        self.period = period
        self.__stop_trading = threading.Event()
    
    def __start_trading(self):
        print('Started', self.account.account_id, 'trader bot')
        while not self.__stop_trading.is_set():
            for trade in self.strategy.get_symbols_to_trade():
                if self.account.is_in_potfolio(trade['symbol']) or trade['symbol'] in self.account.get_open_orders('buy'):
                    continue
                if trade['order_class'] == 'bracket':
                    buy_amount = config['algo_params']['buy_amount']
                    n_shares = math.floor(buy_amount/trade['limit_price'])
                    print("Creating a bracket order...")
                    self.account.create_bracket_order(
                        trade['symbol'], n_shares, trade['side'], 
                        trade['type'], trade['time_in_force'], 
                        take_profit_limit_price=trade['limit_price'], 
                        stop_loss_stop_price=trade['stop_price']
                        )
            time.sleep(self.period)

        print('Stopped', self.account.account_id, 'trader bot')
        return None
    def start(self):
        trading_thread = threading.Thread(target = self.__start_trading)
        trading_thread.start()
    def stop(self):
        self.__stop_trading.set()