import time
import numpy as np
import sys
import pandas as pd

sys.path.insert(0,'modules')
from database import Database

class Strategy:
    def __init__(self, db_conn, buy_strategy, sell_strategy, **kwargs):
        self.means = {}
        self.symbols_to_trade = []
        self.db_conn = db_conn
        self.buy_strategy = buy_strategy
        self.sell_strategy = sell_strategy
        self.window_len = kwargs.get('window_len')
        self.lookback_len = kwargs.get('lookback_len')
        self.stop_threshold = kwargs.get('stop_threshold')
        self.profit_margin = kwargs.get('profit_margin')
        self.buy_threshold = kwargs.get('buy_threshold')
    
    def calculate_means(self, window_len, buffer_size, symbol):
        """Calculates moving averages for the symbol
        The function shall be called periodically from the same place 
        Args:
            db_conn (sqlite3.connect): database connection object
            window_length (int): moving average window length
            buffer_size (int): size of buffer storing moving averages
            symbol (string): symbol of a financial instrument
        Raises:
            ValueError: not enough data in the database for calculating moving averages
        Returns:
            means (np.array): moving averages for the symbol
        """
        df = Database.get_last_n_prices(self.db_conn, symbol, window_len)
        # if not enough data for moving average calculation or wrong timestamps
        if len(df.index) < window_len:
            raise ValueError("Not suitable data for moving average calculation")
        mean = df['close_price'].mean()

        # check if symbol appears for the first time
        if symbol in self.means:
            # Check if means list is full
            assert (len(self.means[symbol]) <= buffer_size)
            # add incoming mean value
            self.means[symbol].append(mean)
            # remove oldest mean if we have overflow
            if len(self.means[symbol]) > buffer_size:
                self.means[symbol].pop(0)
        else: # append to the dataframe if symbol appears first time
            self.means[symbol] = [mean]

        return np.asarray(self.means[symbol])

    def buy_strategy_first_momentum(self, window_len, lookback_len, profit_margin, stop_threshold):
        # do calculations for all symbol
        for symbol in Database.get_all_symbols(self.db_conn):
            try:
                means = self.calculate_means(window_len, lookback_len + 1, symbol)
            # ignore symbol if means are not calculated yet
            except ValueError:
                continue
            # wait until enough moving average values are calculated
            if means.size < lookback_len + 1:
                continue
            deltas_means = np.diff(means)
            # check if momentum is changing to positive direction
            if np.all(np.all(deltas_means[1:] > deltas_means[:-1])):
                order = {
                'symbol':symbol, 
                'side':'buy', 
                'type':'market', 
                'time_in_force':'gtc', 
                'limit_price': (1+profit_margin)*means[-1], 
                'stop_price': (1-stop_threshold)*means[-1], 
                'order_class':'bracket'}
                self.symbols_to_trade.append(order)
            
        return None

    def buy_strategy_moving_average(self, window_len, lookback_len, buy_threshold, profit_margin, stop_threshold):
        # do calculations for all symbol
        for symbol in Database.get_all_symbols(self.db_conn):
            # ignore symbol if there is already open buy
            try:
                means = self.calculate_means(window_len, lookback_len + 1, symbol)
            # ignore symbol if means are not calculated yet
            except ValueError:
                continue
            # wait until enough moving average values are calculated
            if means.size < lookback_len + 1:
                continue
            # check if momentum is changing to positive direction
            if means[-1] - means[0] >= buy_threshold*means[0]:
                order = {
                'symbol': symbol, 
                'side': 'buy', 
                'type': 'market', 
                'time_in_force': 'gtc', 
                'limit_price': (1+profit_margin)*means[-1], 
                'stop_price': (1-stop_threshold)*means[-1], 
                'order_class': 'bracket'}
                self.symbols_to_trade.append(order)
            
        return None

    def get_symbols_to_trade(self):
        self.symbols_to_trade = []
        if self.buy_strategy == 'first_momentum' and self.sell_strategy == 'limit':
            self.buy_strategy_first_momentum(self.window_len, self.lookback_len, self.profit_margin, self.stop_threshold)
        elif self.buy_strategy == 'moving_average' and self.sell_strategy == 'limit':
            self.buy_strategy_moving_average(self.window_len, self.lookback_len, self.buy_threshold, self.profit_margin, self.stop_threshold)
        return self.symbols_to_trade

