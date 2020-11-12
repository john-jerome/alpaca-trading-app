import sqlite3
import pandas as pd

from datetime import datetime, timedelta
from sqlite3 import Error

class Database():
    def __init__(self, db_file):
        self.db_file = db_file

    def get_last_N_prices():
        pass

    def get_all_isin():
        pass

    def prices_cleanup():
        pass
    
    def create_connection():
        """Сreate a database connection to a SQLite database """
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)

        return conn

    def select_data(conn, select_query):
        """Execute a select query on the database."""

        rows = []

        try:
            c = conn.cursor()
            c.execute(select_query)
            rows = c.fetchall()    
        except Error as e:
            print(e)
        
        return rows

    def insert_one_row(conn, row, table):
        """[summary]

        Args:
            conn ([type]): [description]
            row ([type]): [description]
            table ([type]): [description]

        Returns:
            [type]: [description]
        """
        l = len(row)

        values = '?'+',?'*(l-1)

        sql = ''' INSERT INTO {}
                VALUES({}) '''.format(table, str(values))
        
        cur = conn.cursor()

        try:
            cur.execute(sql, row)
            conn.commit()
        except Error as e:
            print(e)

        return None

    def close_connection(conn):

        try:
            conn.close()
        except Error as e:
            print(e)

        return None

    def generate_ts(delay_minutes = 0):
        """Generate current local timestamp."""

        current_ts = datetime.now() + timedelta(minutes=delay_minutes)

        return current_ts

    def unix_to_ts(unix_date):
        """Conver unix date to timestamp."""

        ts = datetime.fromtimestamp(unix_date).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        return ts

    def ts_to_unix(ts):
        """Convert timestamp to unix date."""

        unix_date = datetime.timestamp(ts)

        return unix_date
