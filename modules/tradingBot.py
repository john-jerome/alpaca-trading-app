import threading
import time
import configparser
import sys
import math

sys.path.insert(0,'modules')

from strategy import Strategy
from database import Database
from portfolio import Portfolio
from helpers import is_market_open, time_to_market_close, time_to_market_open

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
        while is_market_open() and (not self.__stop_trading.is_set()):
            # if less than 30 minutes to market close then close all positions and stop the program
            if time_to_market_close() < 30:
                print('Market will close soon. Sell all positions and close all positions before market close')
                self.account.cancel_all_orders()
                self.account.liquidate_all_positions()
                self.stop()
            for trade in self.strategy.get_symbols_to_trade():
                # ignore the symbol if it is in already in the portoflio or we have a pending open order 
                if self.account.is_in_potfolio(trade['symbol']) or trade['symbol'] in self.account.get_open_orders('buy'):
                    continue
                if trade['order_class'] == 'simple':
                    pass
                elif trade['order_class'] == 'bracket':
                    buy_amount = config.getint('algo_params', 'buy_amount')
                    n_shares = math.floor(buy_amount/trade['limit_price'])
                    print("Creating a bracket order for {}...".format(trade['symbol']))
                    print(trade)
                    self.account.create_bracket_order(
                        trade['symbol'], n_shares, trade['side'], 
                        trade['type'], trade['time_in_force'], 
                        take_profit_limit_price=trade['limit_price'], 
                        stop_loss_stop_price=trade['stop_price']
                        )
                elif trade['order_class'] == 'oco':
                    pass
                elif trade['order_class'] == 'oto':
                    pass
                else:
                    print('Specified order class does not exist')
                    self.stop()
            time.sleep(self.period)

        print('Stopped', self.account.account_id, 'trader bot')
        return None
    def start(self):
        trading_thread = threading.Thread(target = self.__start_trading)
        trading_thread.start()
    def stop(self):
        self.__stop_trading.set()