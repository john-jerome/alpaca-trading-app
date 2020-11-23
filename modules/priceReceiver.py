import threading
import time
import websocket
import json
import sys
import os

sys.path.insert(0,'modules')

from helpers import unix_to_ts, is_market_open, generate_ts
from database import Database

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
                "key_id": os.environ['APCA_API_KEY_ID'],
                "secret_key": os.environ['APCA_API_SECRET_KEY']
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

        msg = json.loads(message)
        if 'AM' in msg['stream']:
            row = (
                msg['data']['ev'],
                msg['data']['T'],
                msg['data']['v'],
                msg['data']['av'],
                msg['data']['op'],
                msg['data']['vw'],
                msg['data']['o'],
                msg['data']['h'],
                msg['data']['l'],
                msg['data']['c'],
                msg['data']['a'],
                unix_to_ts(msg['data']['s'] / 1000.0),
                unix_to_ts(msg['data']['e'] / 1000.0),
                generate_ts()
                )
            Database.insert_one_row(self.db_conn, row, table_name = 'alpaca.prices_bars')
            
    def on_close(self, ws):
        print("closed connection")

    def on_error(self, ws, error):
        print(error)

    def __receive_data(self, stop_event):

        self.db_conn = Database.create_connection(self.database_uri)
        while is_market_open() and (not stop_event.is_set()):
            self.ws = websocket.WebSocketApp(
                self.websocket_url, 
                on_open=lambda ws: self.on_open(ws), 
                on_message=lambda ws,message: self.on_message(ws, message), 
                on_close=lambda ws: self.on_close(ws),
                on_error= lambda ws,error: self.on_error(ws, error),
                )
            self.ws.run_forever()
        print('Stop receiving data from', self.websocket_url)

