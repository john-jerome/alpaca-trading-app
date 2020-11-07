import threading
import sys
import configparser

sys.path.insert(0,'modules')
from tg_notifications import send_state
from helpers import prices_cleanup
from database import create_connection
from tradingBot import TradingBot

def main():

  program_state = 'Shutdown'
  print("Starting the program...")
  config = configparser.ConfigParser()
  config.read('config.ini')
  db = config['sqlite']['database']
  
  period_buy = config.getint('thread_params', 'period_buy') # in seconds
  period_sell = config.getint('thread_params', 'period_sell') # in seconds
  period_verify = config.getint('thread_params', 'period_verify') # in seconds
  window_len = config.getint('algo_params', 'window_length')
  lookback_len = config.getint('algo_params', 'lookback_length')
  stop_loss = config.getfloat('algo_params', 'stop_loss_threshold')
  profit_margin = config.getfloat('algo_params', 'profit_margin')
  buy_amount = config.getint('algo_params', 'buy_amount')
  buy_threshold = config.getfloat('algo_params', 'buy_threshold')

  try:
    strategy_buy = {'algorithm':'moving_average', 'period': period_buy, 'buy_amount': buy_amount, 'window_len': window_len, 'lookback_len': lookback_len, 'buy_threshold': buy_threshold}
    strategy_sell = {'algorithm':'limit', 'period': period_sell, 'stop_loss': stop_loss, 'profit_margin': profit_margin}
    # Create threads: receive and write to database; buy stocks; sell stocks; verify open orders
    trading_algo = TradingBot(strategy_buy, strategy_sell)
    trading_algo.start()

    # watchdog for the program
    while True:
      number_of_threads = config.getint('thread_params', 'number_of_threads')
      if program_state == 'Shutdown' and threading.active_count() == number_of_threads:
        print("Program started normally")
        program_state = 'Normal'
        # send telegram notification
        send_state("started")
      if program_state == 'Normal' and threading.active_count() != number_of_threads:
        print("An error occured. Program is terminating...")
        trading_algo.stop()
        program_state = 'Stopping'
      if program_state == 'Stopping' and threading.active_count() == 1:
        program_state = 'Shutdown'
        print("Program terminated")
        prices_cleanup(create_connection(db))
        send_state("stopped")
        break
  except KeyboardInterrupt:
    prices_cleanup(create_connection(db))
    send_state("manually stopped")

if __name__== "__main__":
  main()