import requests
import pandas as pd
import json
import sys

sys.path.insert(0,'modules')

from database import create_connection, insert_one_row, select_data, close_connection, generate_ts

api_key = "e33d9b7419949ca3cf1665591c918e48bd0f7523"
headers = {
    'Authorization': 'Token ' + str(api_key)}

database = r"alpaca.db"
conn = create_connection(database)

for i in range(0,41):
  url = "https://api.lemon.markets/rest/v1/data/instruments/?limit=1000&offset=" + str(i*1000)
  payload = {}
  response = requests.request("GET", url, headers=headers, data = payload)
  dict = response.json()['results']
  for item in dict:

      item['updated_at'] = generate_ts()
      item['is_current'] = 0

      row = (
          item['isin'],
          item['title'],
          item['wkn'],
          item['type'],
          item['symbol'],
          item['updated_at'],
          item['is_current']
      )
      insert_one_row(conn, row, table='instruments')

