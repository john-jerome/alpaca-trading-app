import threading
import time
import websocket
import json
import sys
import os

class TradeUpdates:

    def __init__(self, websocket_url):
        self.__stop_trade_updates = threading.Event()
        self.websocket_url = websocket_url

    def start(self):
        trade_updates_thread = threading.Thread(target = self.__trade_updates, args=(self.__stop_trade_updates,))
        trade_updates_thread.start()

    def stop(self):
        self.__stop_trade_updates.set()
    
    def on_open(self, ws):

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
        print(msg)
            
    def on_close(self, ws):
        print("closed connection")

    def on_error(self, ws, error):
        print(error)

    def __trade_updates(self, stop_event):

        while not stop_event.is_set():
            self.ws = websocket.WebSocketApp(
                self.websocket_url, 
                on_open=lambda ws: self.on_open(ws), 
                on_message=lambda ws,message: self.on_message(ws, message), 
                on_close=lambda ws: self.on_close(ws),
                on_error= lambda ws,error: self.on_error(ws, error),
                )
            self.ws.run_forever()
    

tradeReceiver = TradeUpdates("https://paper-api.alpaca.markets/stream")
tradeReceiver.start()