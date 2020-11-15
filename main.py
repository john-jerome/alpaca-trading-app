import threading
import sys
import configparser

sys.path.insert(0,'modules')
from telegramBot import send_state
from helpers import prices_cleanup
from database import create_connection
from tradingBot import TradingBot

config = configparser.ConfigParser()
config.read('config.ini')

headers = {
  'APCA-API-KEY-ID': config['alpaca-paper']['APCA_API_KEY_ID'],
  'APCA-API-SECRET-KEY': config['alpaca-paper']['APCA_API_SECRET_KEY']
}

def main():

  program_state = 'Shutdown'
  print('Starting the program...')
  config = configparser.ConfigParser()
  config.read('config.ini')
  db = config['sqlite']['database']

  strategy_buy = {'algorithm':'moving_average', 
                'period'        : config.getint('thread_params', 'period_buy'), 
                'buy_amount'    : config.getint('algo_params', 'buy_amount'), 
                'window_len'    : config.getint('algo_params', 'window_length'), 
                'lookback_len'  : config.getint('algo_params', 'lookback_length'), 
                'buy_threshold' : config.getfloat('algo_params', 'buy_threshold'),
                'stop_loss'    : config.getfloat('algo_params', 'stop_loss_threshold'),
                'profit_margin': config.getfloat('algo_params', 'profit_margin')}

  strategy_sell = {'algorithm': 'no_algo'}
  try:
    # Create threads: receive and write to database; buy stocks; sell stocks; verify open orders
    trading_bot = TradingBot(strategy_buy, strategy_sell)
    trading_bot.start()

    # watchdog for the program
    while True:
      number_of_threads = config.getint('thread_params', 'number_of_threads')
      if program_state == 'Shutdown' and threading.active_count() == number_of_threads:
        print('Program started normally')
        program_state = 'Normal'
        # send telegram notification
        send_state('started')
      if program_state == 'Normal' and threading.active_count() != number_of_threads:
        print('An error occured. Program is terminating...')
        trading_bot.stop()
        program_state = 'Stopping'
      if program_state == 'Stopping' and threading.active_count() == 1:
        program_state = 'Shutdown'
        print('Program terminated')
        prices_cleanup(create_connection(db))
        send_state('stopped')
        break
  except KeyboardInterrupt:
    prices_cleanup(create_connection(db))
    send_state('manually stopped')

if __name__== "__main__":
  main()