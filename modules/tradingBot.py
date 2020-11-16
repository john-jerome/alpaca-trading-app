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
    
    def __start_trading(self):
        db_conn = Database.create_connection(self.database_uri)
        with db_conn:
            while not self.__stop_trading.is_set():
                for trade in self.strategy.get_symbols_to_trade(db_conn):
                    account.create_bracket_order(trade)
                time.sleep(self.period)

        close_connection(db_conn)
        print("Stop trading ...")
        return None

    def start(self):
        trading_thread = threading.Thread(target = self.__start_trading)        
        trading_thread.start()
    
    def stop(self):
        self.__stop_trading.set()
    
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