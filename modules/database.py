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
            rows = cursor.fetchall()    
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        
        df = pd.DataFrame(rows)
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
        values = '?'+',?'*(l-1)
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



    
