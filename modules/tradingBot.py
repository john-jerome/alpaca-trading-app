import threading
import time
import weakref
import configparser
import sys
from enum import Enum

sys.path.insert(0,'modules')
from websocket_conn import receive_data
from algorithms import verify_orders, buy_strategy_moving_average, sell_strategy_limit, buy_strategy_first_momentum
from database import create_connection, close_connection

config = configparser.ConfigParser()
config.read('config.ini') 
db = config['sqlite']['database']

class TradingBot(object):
    def __init__(self, strategy_buy, strategy_sell, period_verify = 30):
        self.__stop_verifying_orders = threading.Event()
        self.__stop_buying = threading.Event()
        self.__stop_selling = threading.Event()
        self.strategy_buy = strategy_buy
        self.strategy_sell = strategy_sell
        self.period_verify = period_verify

    def __start_receiving_data(self):
        receive_data_thread = threading.Thread(target = receive_data, args=(self.__stop_receiving_data, ))
        receive_data_thread.start()
    
    def __start_verifying_orders(self):
        verify_orders_thread = threading.Thread(target = verify_orders, args=(self.__stop_verifying_orders, self.period_verify, ))
        verify_orders_thread.start()

    def __start_buying(self):
        db_conn = create_connection(db)
        with db_conn:
            while not self.__stop_buying.is_set():
                if self.strategy_buy['algorithm'] == 'moving_average':
                    buy_strategy_moving_average(db_conn, self.strategy_buy['buy_amount'], self.strategy_buy['window_len'], self.strategy_buy['lookback_len'], self.strategy_buy['buy_threshold'])
                elif self.strategy_buy['algorithm'] == 'first_momentum':
                    buy_strategy_first_momentum(db_conn, self.strategy_buy['buy_amount'], self.strategy_buy['window_len'], self.strategy_buy['lookback_len'], self.strategy_buy['buy_threshold'])
                else:
                    print("The specified buy algorithm does not exist")
                    self.stop()
                time.sleep(self.strategy_buy['period'])

        close_connection(db_conn)
        print("Stop buying stocks...")
        return None
    
    def __start_selling(self):
        db_conn = create_connection(db)
        with db_conn:
            while not self.__stop_selling.is_set():
                if self.strategy_sell['algorithm'] == 'limit':
                    pass
                else:
                    print("The specified sell algorithm does not exist")
                    self.stop()
                time.sleep(self.strategy_sell['period'])

        close_connection(db_conn)
        print("Stop selling stocks...")
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
        self.__stop_buying.set()
        self.__stop_selling.set()
        self.__stop_verifying_orders.set()