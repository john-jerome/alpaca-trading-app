from modules.algorithms import is_open_sell_order
from modules.database import create_connection, select_data, generate_ts, ts_to_unix, unix_to_ts
from modules.orders import get_current_portfolio
from modules.helpers import get_last_N_prices, prices_cleanup
import websocket
import json
import configparser
import requests
import json


config = configparser.ConfigParser()
config.read('config.ini')

db = config['sqlite']['database']

db_conn = create_connection(db)

prices_cleanup(db_conn)
