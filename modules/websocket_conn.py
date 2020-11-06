import websocket
import json
import threading
import time
import configparser
import sys

sys.path.insert(0,'modules')

from database import create_connection, insert_one_row, select_data, close_connection, unix_to_ts
from helpers import get_all_isin

config = configparser.ConfigParser()
config.read('config.ini')

db = config['sqlite']['database']
websocket_endpoint = str(config['lemon-markets']['websocket_endpoint'])

def websocket_connect(websocket_endpoint):

    ws = websocket.WebSocket()
    ws.connect(websocket_endpoint)

    return ws

def receive_data(stop_event):
    """[summary]

    Args:
        stop_event ([type]): [description]

    Returns:
        [type]: [description]
    """

    db_conn = create_connection(db)

    ws = websocket_connect(websocket_endpoint)
    timeout = config.getint('websocket_params', 'timeout')
    ws.settimeout(timeout)

    for isin in get_all_isin(db_conn):
        ws.send(json.dumps({"action": "subscribe",  "specifier": "with-price", "value": isin}))
    with db_conn:
        while not stop_event.is_set():
            try:
                
                response = json.loads(ws.recv())
                response['timestamp'] = unix_to_ts(response['date'])

                if response['bid_price'] > 0.0 and response['ask_price'] > 0.0:
                    relative_spread = round(((response['ask_price'] - response['bid_price'])/response['bid_price']) * 100, 2)
                    row = (
                        response['isin'], 
                        response['bid_price'], 
                        response['ask_price'], 
                        relative_spread, 
                        response['timestamp']
                        )
                    insert_one_row(db_conn, row, table = 'prices')

            except Exception as e:
                print("Websocket error:", e)
                break

    close_connection(db_conn)
    print("Stop receiving data...")
    return None
