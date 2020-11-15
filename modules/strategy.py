import time
import math
import numpy as np
from modules.database import Database

class Strategy:
    def __init__(self, db_conn, buy_strategy, sell_strategy):
        self.means = {}
        self.trading_list = []
        self.db_conn = db_conn
        self.buy_strategy = buy_strategy
        self.sell_strategy = sell_strategy
    
    def calculate_means(db_conn, window_length, buffer_size, isin):
        """Calculates moving averages for the isin
        The function shall be called periodically from the same place 
        Args:
            db_conn (sqlite3.connect): database connection object
            window_length (int): moving average window length
            buffer_size (int): size of buffer storing moving averages
            isin (string): isin of a financial instrument
        Raises:
            ValueError: not enough data in the database for calculating moving averages
        Returns:
            means (np.array): moving averages for the isin
        """
        df = get_last_N_prices(self.db_conn, isin, window_length)
        # if not enough data for moving average calculation or wrong timestamps
        if len(df.index) < window_length:
            raise ValueError("Not suitable data for moving average calculation")
        mean = df['ask_price'].mean()

        # block to save data for analytics in mean_analysis
        if isin in isin_for_analysis:
            latest_timestamp = df.iloc[0]['date']
            row = (
                isin,
                mean.item(),
                latest_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            )
            Database.insert_one_row(db_conn, row, table = 'mean_analysis')
        # check if isin appears for the first time
        if isin in self.means:
            # Check if means list is full
            assert (len(self.means[isin]) <= buffer_size)
            # add incoming mean value
            self.means[isin].append(mean)
            # remove oldest mean if we have overflow
            if len(self.means[isin]) > buffer_size:
                self.means[isin].pop(0)
        else: # append to the dataframe if isin appears first time
            self.means[isin] = [mean]

        return np.asarray(self.means[isin])

    def buy_strategy_first_momentum(db_conn, window_length, lookback_len, account):
        # do calculations for all isin
        for isin in get_all_isin(db_conn):
            # ignore isin if there is already open buy
            status, _ = is_open_buy_order(db_conn, isin)
            if status or is_in_potfolio(db_conn, isin):
                continue
            try:
                means = calculate_means(db_conn, window_length, lookback_len + 1, isin)
            # ignore isin if means are not calculated yet
            except ValueError:
                continue
            # wait until enough moving average values are calculated
            if means.size < lookback_len + 1:
                continue
            deltas_means = np.diff(means)
            # check if momentum is changing to positive direction
            if np.all(np.all(deltas_means[1:] > deltas_means[:-1])):
                self.trading_list.append({'stock':isin, 'trade_type': 'bracket'})
                #buy_shares(db_conn, isin, buy_amount, minutes_valid = 5)
            
        return None

    def buy_strategy_moving_average(db_conn, buy_amount, window_length, lookback_len, buy_threshold, account):
        # do calculations for all isin
        for isin in get_all_isin(db_conn):
            # ignore isin if there is already open buy
            status, _ = is_open_buy_order(db_conn, isin)
            if status or is_in_potfolio(db_conn, isin):
                continue
            try:
                means = calculate_means(db_conn, window_length, lookback_len + 1, isin)
            # ignore isin if means are not calculated yet
            except ValueError:
                continue
            # wait until enough moving average values are calculated
            if means.size < lookback_len + 1:
                continue
            # check if momentum is changing to positive direction
            if means[-1] - means[0] >= buy_threshold*means[0]:
                self.trading_list.append({'stock':isin, 'trade_type': 'bracket'})
                #buy_shares(db_conn, isin, buy_amount, minutes_valid = 5)
        
        return None

    def get_trades(self):
        trading_list = []
        if buy_strategy == 'first_momentum' and sell_strategy == 'limit':
            buy_strategy_first_momentum()
        return trading_list 
