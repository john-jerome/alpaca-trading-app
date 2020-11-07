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
    def __init__(self, strategy_buy, strategy_sell, period_buy = 45, period_sell = 45, period_verify = 30, *args, **kwargs):
        self.__stop_receiving_data = threading.Event()
        self.__stop_verifying_orders = threading.Event()
        self.__stop_buying = threading.Event()
        self.__stop_selling = threading.Event()
        self.strategy_buy = strategy_buy
        self.strategy_sell = strategy_sell
        self.period_verify = period_verify # seconds
        self.period_buy = period_buy # seconds
        self.period_sell = period_sell # seconds
        self.window_length = kwargs.get('window_length', None)
        self.lookback_length = kwargs.get('lookback_length', None)

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
                if self.strategy_buy == 'moving_average':
                    assert (self.window_length != None), "Window length is required"
                    assert (self.lookback_length != None), "Lookback length is required"
                    buy_strategy_moving_average(db_conn, self.window_length, self.lookback_length)
                elif self.strategy_buy == 'first_momentum':
                    assert (self.window_length != None), "Window length is required"
                    assert (self.lookback_length != None), "Lookback length is required"
                    buy_strategy_first_momentum(db_conn, self.window_length, self.lookback_length)
                else:
                    print("The specified buy strategy does not exist")
                    self.stop()
                time.sleep(self.period_buy)

        close_connection(db_conn)
        print("Stop buying stocks...")
        return None
    
    def __start_selling(self):
        db_conn = create_connection(db)
        with db_conn:
            while not self.__stop_selling.is_set():
                if self.strategy_sell == 'limit':
                    sell_strategy_limit(db_conn)
                else:
                    print("The specified sell strategy does not exist")
                    self.stop()
                time.sleep(self.period_sell)

        close_connection(db_conn)
        print("Stop selling stocks...")
        return None

    def start(self):
        buy_thread = threading.Thread(target = self.__start_buying)
        sell_thread = threading.Thread(target = self.__start_selling)
        
        self.__start_receiving_data()
        self.__start_verifying_orders()
        buy_thread.start()
        sell_thread.start()
    
    def stop(self):
        self.__stop_receiving_data.set()
        self.__stop_buying.set()
        self.__stop_selling.set()
        self.__stop_verifying_orders.set()