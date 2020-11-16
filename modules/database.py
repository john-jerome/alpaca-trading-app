import psycopg2
import os
import pandas as pd
import configparser
import sys
from datetime import datetime, timedelta

sys.path.insert(0,'modules')

config = configparser.ConfigParser()
config.read('config.ini') 
database_uri = config['database']['database_uri']

class Database:
    
    @staticmethod
    def create_connection(database_uri):
        """[summary]

        Returns:
            [type]: [description]
        """
    
        try:
            conn = psycopg2.connect(database_uri, sslmode='require')
        except (Exception, psycopg2.DatabaseError) as error:
            conn = None
            print(error)

        return conn
        
    @staticmethod
    def select_data(conn, select_query):
        """[summary]

        Args:
            conn ([type]): [description]
            select_query ([type]): [description]

        Returns:
            [type]: [description]
        """

        rows = []

        try:
            cursor = conn.cursor()
            cursor.execute(select_query)
            colnames = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        
        df = pd.DataFrame(rows, columns = colnames)

        return df

    @staticmethod
    def get_last_n_prices(conn, symbol, N):
        """Create a df containing last N prices for a specific isin.

        Args:
            conn: db connection object
            symbol (string): symbol of a stock
            N (int): number of prices to query

        Returns:
            pandas DataFrame: resulting dataframe
        """

        sql_select_last_N = """
        SELECT * 
        FROM alpaca.prices_bars
        WHERE symbol = '{}'
        ORDER BY window_end DESC 
        LIMIT {} ;""".format(symbol, N)

        df = Database.select_data(conn, sql_select_last_N)
        df['window_start'] = pd.to_datetime(df['window_start'], format="%Y-%m-%d %H:%M:%S")
        df['window_end'] = pd.to_datetime(df['window_end'], format="%Y-%m-%d %H:%M:%S")
        
        return df
        
    @staticmethod
    def get_all_symbols(conn):

        sql_select_symbols = """
        SELECT DISTINCT symbols 
        FROM alpaca.trading_list
        WHERE exchange in ('Nasdaq Global Select', 'New York Stock Exchange', 'NYSE', 'NYSE Arca');"""

        df = Database.select_data(conn, sql_select_symbols)

        return df

    @staticmethod
    def insert_one_row(conn, row, table_name):
        """[summary]

        Args:
            conn ([type]): database connection object
            row ([type]): row of data to insert
            table_name ([type]): table name

        Returns:
            None
        """

        l = len(row)
        values = '%s'+',%s'*(l-1)
        sql = """ INSERT INTO {}
                VALUES({}) """.format(table_name, str(values))

        try:
            cursor = conn.cursor()
            cursor.execute(sql, row)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return None

    @staticmethod
    def close_connection(conn):

        try:
            conn.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return None



    
