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
  program_state = 'Init'
  
  period_buy = config.getint('thread_params', 'period_buy') # in seconds
  period_sell = config.getint('thread_params', 'period_sell') # in seconds
  period_verify = config.getint('thread_params', 'period_verify') # in seconds

  try:
    # Create threads: receive and write to database; buy stocks; sell stocks; verify open orders
    trading_algo = Strategy(strategy_buy="moving_average", strategy_sell="limit", period_buy = period_buy, period_sell = period_sell)
    trading_algo.window_length = config.getint('algo_params', 'window_length')
    trading_algo.lookback_length = lookback_length = config.getint('algo_params', 'lookback_length')
    trading_algo.start()

    # watchdog for the program
    while True:
      number_of_threads = config.getint('thread_params', 'number_of_threads')
      if program_state == 'Init' and threading.active_count() == number_of_threads:
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