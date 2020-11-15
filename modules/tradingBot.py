import threading
import time
import weakref
import configparser
import sys
from enum import Enum

sys.path.insert(0,'modules')
from websocket_conn import receive_data
from strategy import Strategy
from database import Database

config = configparser.ConfigParser()
config.read('config.ini') 
db = config['sqlite']['database']

class TradingBot():
    def __init__(self, strategy_buy, strategy_sell, account, strategy):
        self.__stop_trading = threading.Event()
        self.strategy_buy = strategy_buy
        self.strategy_sell = strategy_sell
        self.account = account
        self.strategy = strategy
    
    def __start_verifying_orders(self):
        verify_orders_thread = threading.Thread(target = verify_orders, args=(self.__stop_verifying_orders, self.period_verify, ))
        verify_orders_thread.start()
    
    def __start_trading(self):
        db_conn = create_connection(db)
        with db_conn:
            while not self.__stop_trading.is_set():
                if self.strategy_buy['algorithm'] == 'moving_average':
                    self.strategy.get_trading
                time.sleep(self.strategy_buy['period'])

        close_connection(db_conn)
        print("Stop buying stocks...")
        return None

    def start(self):
        buy_thread = threading.Thread(target = self.__start_buying)
        if 'algorithm' in self.strategy_sell and self.strategy_sell['algorithm'] != 'no_algo':
            sell_thread = threading.Thread(target = self.__start_selling)
        
        self.__start_receiving_data()
        self.__start_verifying_orders()
        buy_thread.start()
        sell_thread.start()
    
    def stop(self):
        self.__stop_trading.set()
        self.__stop_verifying_orders.set()
    
    def buy_shares(db_conn, isin, buy_amount, minutes_valid):
        print("Executing an order... buy isin:", isin)
        # buy: number of shares based on moving average price, valid for 5 minutes
        try:
            latest_stock_price = get_last_N_prices(db_conn, isin, 1).iloc[0]['bid_price']
            n_shares = math.floor(buy_amount/latest_stock_price)
            create_order(db_conn, isin, "buy", n_shares, ts_to_unix(generate_ts(minutes_valid)), "market", limit_price = None, stop_price = None)
        except:
            print("Buying shares failed")

        return None