import threading
import time
import configparser
import websocket
import json
from database import Database

config = configparser.ConfigParser()
config.read('config.ini')

APCA_API_BASE_URL = config['alpaca-paper']['APCA_API_BASE_URL']
APCA_API_KEY_ID = config['alpaca-paper']['APCA_API_KEY_ID']
APCA_API_SECRET_KEY = config['alpaca-paper']['APCA_API_SECRET_KEY']

class Receiver:

    def __init__(self, websocket_url, database_uri, period):
        self.__stop_receiving_data = threading.Event()
        self.websocket_url = websocket_url
        self.database_uri = database_uri
        self.__period = period

    def start(self):
        receive_data_thread = threading.Thread(target = self.__receive_data, args=(self.__stop_receiving_data, ))
        receive_data_thread.start()

    def stop(self):
        self.__stop_receiving_data.set()

    def __write_to_db(self, db_conn):
        pass
    
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

        return status

    def __receive_data(self, stop_event, symbol_list):

        conn = Database.create_connection(self.database_uri)
        ws = self.ws_authenticate()
        with conn:
            while not self.__stop_receiving_data.is_set():
                payload = {
                    "action": "listen",
                    "data": {
                        "streams": ["AM.SPY"]
                        }
                    }
                ws.send(json.dumps(payload))
                response = json.loads(ws.recv())

                row = (

                )

                Database.insert_one_row(conn, row, table_name = 'alpaca.prices_bars')
