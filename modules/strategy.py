import time
import numpy as np
import sys

sys.path.insert(0,'modules')
from database import Database

class Strategy:
    def __init__(self, db_conn, buy_strategy, sell_strategy):
        self.means = {}
        self.symbols_to_trade = []
        self.db_conn = db_conn
        self.buy_strategy = buy_strategy
        self.sell_strategy = sell_strategy
    
    def calculate_means(window_length, buffer_size, symbol):
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
        df = get_last_N_prices(self.db_conn, symbol, window_length)
        # if not enough data for moving average calculation or wrong timestamps
        if len(df.index) < window_length:
            raise ValueError("Not suitable data for moving average calculation")
        mean = df['ask_price'].mean()

        # block to save data for analytics in mean_analysis
        if symbol in symbol_for_analysis:
            latest_timestamp = df.iloc[0]['date']
            row = (
                symbol,
                mean.item(),
                latest_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            )
            Database.insert_one_row(self.db_conn, row, table = 'mean_analysis')
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

    def buy_strategy_first_momentum(window_length, lookback_len, account):
        # do calculations for all symbol
        for symbol in get_all_symbol(self.db_conn):
            try:
                means = calculate_means(window_length, lookback_len + 1, symbol)
            # ignore symbol if means are not calculated yet
            except ValueError:
                continue
            # wait until enough moving average values are calculated
            if means.size < lookback_len + 1:
                continue
            deltas_means = np.diff(means)
            # check if momentum is changing to positive direction
            if np.all(np.all(deltas_means[1:] > deltas_means[:-1])):
                self.symbols_to_trade.append({'stock':symbol, 'trade_type': 'bracket'})
            
        return None

    def buy_strategy_moving_average(buy_amount, window_length, lookback_len, buy_threshold, account):
        # do calculations for all symbol
        for symbol in get_all_symbol(self.db_conn):
            # ignore symbol if there is already open buy
            try:
                means = calculate_means(window_length, lookback_len + 1, symbol)
            # ignore symbol if means are not calculated yet
            except ValueError:
                continue
            # wait until enough moving average values are calculated
            if means.size < lookback_len + 1:
                continue
            # check if momentum is changing to positive direction
            if means[-1] - means[0] >= buy_threshold*means[0]:
                self.symbols_to_trade.append({'stock':symbol, 'trade_type': 'bracket'})
        
        return None

    def get_symbols_to_trade(self):
        self.symbols_to_trade = []
        if buy_strategy == 'first_momentum' and sell_strategy == 'limit':
            buy_strategy_first_momentum()
        return self.symbols_to_trade 
