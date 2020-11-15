import psycopg2
import os
import pandas as pd
import configparser
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read('config.ini') 
database_uri = config['database']['database_uri']

class Database():
    def __init__(self, database_uri):
        self.database_uri = database_uri
    
    def create_connection(self):
        """[summary]

        Returns:
            [type]: [description]
        """
    
        try:
            conn = psycopg2.connect(self.database_uri, sslmode='require')
        except (Exception, psycopg2.DatabaseError) as error:
            conn = None
            print(error)

        return conn

    def select_data(self, conn, select_query):
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

    def insert_one_row(self, conn, row, table_name):
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
        
        cursor = conn.cursor()

        try:
            cursor.execute(sql, row)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return None

    def close_connection(self, conn):

        try:
            conn.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return None


    
