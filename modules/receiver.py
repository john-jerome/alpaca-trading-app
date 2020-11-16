import threading
import time
import configparser
import websocket
import json
import sys

sys.path.insert(0,'modules')

from helpers import unix_to_ts, is_market_open
from database import Database

config = configparser.ConfigParser()
config.read('config.ini')

APCA_API_BASE_URL = config['alpaca-paper']['APCA_API_BASE_URL']
APCA_API_KEY_ID = config['alpaca-paper']['APCA_API_KEY_ID']
APCA_API_SECRET_KEY = config['alpaca-paper']['APCA_API_SECRET_KEY']

class Receiver:

    def __init__(self, websocket_url, database_uri):
        self.__stop_receiving_data = threading.Event()
        self.websocket_url = websocket_url
        self.database_uri = database_uri

    def start(self):
        receive_data_thread = threading.Thread(target = self.__receive_data, args=(self.__stop_receiving_data, 0,))
        receive_data_thread.start()

    def stop(self):
        self.__stop_receiving_data.set()
    
    def ws_authenticate(self):

        payload = {
            "action": "authenticate",
            "data": {
                "key_id": APCA_API_KEY_ID,
                "secret_key": APCA_API_SECRET_KEY
                }
            }

        ws = websocket.WebSocket()
        ws.connect(self.websocket_url)
        ws.send(json.dumps(payload))
        response = json.loads(ws.recv())

        status = response['data']['status']

        return ws, status

    def __receive_data(self, stop_event, symbol_list):

        conn = Database.create_connection(self.database_uri)
        ws, status = self.ws_authenticate()
        timeout = config.getint('alpaca-paper', 'websocket_timeout')
        ws.settimeout(timeout)

        if status == 'authorized':
            am_symbols = ["AM." + e for e in Database.get_all_symbols(conn)]
            payload = {
                        "action": "listen",
                        "data": {
                            "streams": am_symbols
                            }
                        }
            ws.send(json.dumps(payload))
            with conn:
                while not self.__stop_receiving_data.is_set():
                    try:
                        response = json.loads(ws.recv())
                        print("Websocket: " + response['stream'])
                        if response['stream'] != 'listening':
                            row = (
                                response['data']['ev'],
                                response['data']['T'],
                                response['data']['v'],
                                response['data']['av'],
                                response['data']['op'],
                                response['data']['vw'],
                                response['data']['o'],
                                response['data']['h'],
                                response['data']['l'],
                                response['data']['c'],
                                response['data']['a'],
                                unix_to_ts(response['data']['s'] / 1000.0),
                                unix_to_ts(response['data']['e'] / 1000.0)
                            )
                            Database.insert_one_row(conn, row, table_name = 'alpaca.prices_bars')
                    except Exception as e:
                        print("Websocket error:", e)
                        break