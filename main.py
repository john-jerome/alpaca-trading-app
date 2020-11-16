import configparser
import sys

sys.path.insert(0,'modules')
from strategy import Strategy
from tradingBot import TradingBot
from portfolio import Portfolio
from database import Database
from receiver import Receiver



config = configparser.ConfigParser()
config.read('config.ini')

db = config['database']['database_uri']
db_conn = Database.create_connection(db)
st = Strategy(db_conn, 'moving_average', 'limit', window_len = 5, lookback_len = 7, buy_threshold = 0.01, profit_margin = 0.05, stop_threshold = 0.05)
acc = Portfolio('ua')

rec = Receiver('wss://data.alpaca.markets/stream', db)
bot = TradingBot(db, st, acc, 30)

rec.start()
bot.start()