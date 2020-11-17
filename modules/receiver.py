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

APCA_API_KEY_ID = config['alpaca-paper']['APCA_API_KEY_ID']
APCA_API_SECRET_KEY = config['alpaca-paper']['APCA_API_SECRET_KEY']

class Receiver:

    def __init__(self, websocket_url, database_uri):
        self.__stop_receiving_data = threading.Event()
        self.websocket_url = websocket_url
        self.database_uri = database_uri

    def start(self):
        receive_data_thread = threading.Thread(target = self.__receive_data, args=(self.__stop_receiving_data,))
        receive_data_thread.start()

    def stop(self):
        self.__stop_receiving_data.set()
    
    def on_open(self, ws):

        auth_payload = {
            "action": "authenticate",
            "data": {
                "key_id": APCA_API_KEY_ID,
                "secret_key": APCA_API_SECRET_KEY
                }
            }

        ws.send(json.dumps(auth_payload))

        am_symbols = ["AM." + e for e in Database.get_all_symbols(self.db_conn)]
        payload = {
            "action": "listen",
            "data": {
                "streams": am_symbols
                }
                }
        
        ws.send(json.dumps(payload))

    def on_message(self, ws, message):

        print("received a message")
        if 'AM' in message['stream']:
            row = (
                message['data']['ev'],
                message['data']['T'],
                message['data']['v'],
                message['data']['av'],
                message['data']['op'],
                message['data']['vw'],
                message['data']['o'],
                message['data']['h'],
                message['data']['l'],
                message['data']['c'],
                message['data']['a'],
                unix_to_ts(message['data']['s'] / 1000.0),
                unix_to_ts(message['data']['e'] / 1000.0)
                )
            Database.insert_one_row(self.db_conn, row, table_name = 'alpaca.prices_bars')
            
    def on_close(self, ws):
        print("closed connection")

    def __receive_data(self, stop_event):

        self.db_conn = Database.create_connection(self.database_uri)
        while not stop_event.is_set():
            self.ws = websocket.WebSocketApp(
                self.websocket_url, 
                on_open=lambda ws: self.on_open(ws), 
                on_message=lambda ws,message: self.on_message(ws, message), 
                on_close=lambda ws: self.on_close(ws)
                )
            self.ws.run_forever()

