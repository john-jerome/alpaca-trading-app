import threading
import time
import websocket
import json
import sys
import os

from database import Database

class TradeUpdates:

    def __init__(self, websocket_url, database_uri, account_id):
        self.websocket_url = websocket_url
        self.database_uri = database_uri
        self.account_id = account_id
        self.ws = None
    
    def on_open(self, ws):

        if self.account_id == 'ua':

            auth_payload = {
                "action": "authenticate",
                "data": {
                    "key_id": "PKA9J5UADS5Y7UYG89NB",
                    "secret_key": "8om4fiJETeVvqa4m623KANaQL6wOl453djHpNZxf"
                    }
                }

        ws.send(json.dumps(auth_payload))

        payload = {
            "action": "listen",
            "data": {
                "streams": ["trade_updates"]
                }
                }
        
        ws.send(json.dumps(payload))

    def on_message(self, ws, message):

        msg = json.loads(message)
        #Database.insert_one_row(self.db_conn, row, table_name = 'alpaca.prices_bars')
        print(msg)
            
    def on_close(self, ws):
        print("closed connection")

    def on_error(self, ws, error):
        print(error)

    def start(self):
        print('Creating configuration for websocket', self.websocket_url)
        self.ws = websocket.WebSocketApp(
                self.websocket_url, 
                on_open=lambda ws: self.on_open(ws), 
                on_message=lambda ws,message: self.on_message(ws, message), 
                on_close=lambda ws: self.on_close(ws),
                on_error= lambda ws,error: self.on_error(ws, error),
                )
        self.ws.keep_running = True
        print('Starting a thread for websocket', self.websocket_url)
        trade_updates_thread = threading.Thread(target = self.ws.run_forever)
        trade_updates_thread.start()
        print('Start receiving data from', self.websocket_url)

    def stop(self):
        self.ws.keep_running = False
        print('Stop receiving data from', self.websocket_url)
            
        
    
