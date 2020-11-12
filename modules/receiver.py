import threading
import time

class Receiver:
    # argument: database -> Database class connection, period -> period
    def __init__(self, database, period):
        self.__stop_receiving_data = threading.Event()
        self.__period = period
        self.__database = database

    def start(self):
        receive_data_thread = threading.Thread(target = self.__receive_data, args=(self.__stop_receiving_data, ))
        receive_data_thread.start()

    def stop(self):
        self.__stop_receiving_data.set()

    def __write_to_db(self, db_conn):
        pass

    def __receive_data(self, stop_event):
        with self.__database.create_connection():
            while not self.__stop_receiving_data.is_set():
                pass