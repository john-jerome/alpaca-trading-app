import configparser
import sys
import threading
import os

sys.path.insert(0,'modules')

from telegramBot import send_state
from strategy import Strategy
from tradingBot import TradingBot
from portfolio import Portfolio
from database import Database
from priceReceiver import Receiver
from tradeUpdates import TradeUpdates

config = configparser.ConfigParser()
config.read('config.ini')

account_id = 'ua'
db_url = os.environ['DATABASE_URL']
db_conn = Database.create_connection(db_url)

move_av = Strategy(
  db_conn, 'moving_average', 
  'limit', window_len = 5, 
  lookback_len = 7, buy_threshold = 0.01, 
  profit_margin = 0.005, stop_threshold = 0.005)
account = Portfolio(account_id)

tradeReceiver = TradeUpdates(
  "wss://paper-api.alpaca.markets/stream", 
  db_url, account_id)

dataReceiver = Receiver(
  "wss://data.alpaca.markets/stream", db_url)

traderBot = TradingBot(move_av, account, period = 60)

tradeReceiver.start()
dataReceiver.start()
traderBot.start()

number_of_threads = 4
program_state = 'Init'
# watchdog for the program
while True:
  if program_state == 'Init' and threading.active_count() == number_of_threads:
    print('Program started normally')
    program_state = 'Normal'
    # send telegram notification
    send_state('started')
  if program_state == 'Normal' and threading.active_count() != number_of_threads:
    print('An error occured. Program is terminating...')
    dataReceiver.stop()
    traderBot.stop()
    program_state = 'Stopping'
  if program_state == 'Stopping' and threading.active_count() == 1:
    program_state = 'Shutdown'
    Database.close_connection(db_conn)
    print("Program terminated")
    send_state("stopped")
    break