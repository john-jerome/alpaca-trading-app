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
            for trade in self.strategy.get_symbols_to_trade():
                if trade['order_class'] == 'bracket':
                    self.account.create_bracket_order(trade['symbol'], 1, trade['side'], trade['type'], trade['time_in_force'], trade['limit_price'], trade['stop_price'])
            time.sleep(self.period)

        print("Stop trading ...")
        return None
    
    def stop(self):
        self.stop_flag = True
    
    def buy_shares(db_conn, symbol, buy_amount, minutes_valid):
        print("Executing an order... buy symbol:", symbol)
        # buy: number of shares based on moving average price, valid for 5 minutes
        try:
            latest_stock_price = get_last_N_prices(db_conn, symbol, 1).iloc[0]['bid_price']
            n_shares = math.floor(buy_amount/latest_stock_price)
            account.create_bracket_order(db_conn, symbol, "buy", n_shares, ts_to_unix(generate_ts(minutes_valid)), "market", limit_price = None, stop_price = None)
        except:
            print("Buying shares failed")

        return None