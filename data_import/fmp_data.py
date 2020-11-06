import requests
import pandas as pd
import json
import sys

sys.path.insert(0,'modules')

from database import create_connection, insert_one_row, select_data, close_connection, generate_ts

fmp_api_key_ivan = "d63327cc34caf1477ad764813b65fc99"
fmp_api_key_yernar = "751dad58ec056ddb1798da7063a7acb8"
market_cap = 50000000000


url = "https://financialmodelingprep.com/api/v3/stock-screener?marketCapMoreThan={}&apikey={}".format(market_cap, fmp_api_key_ivan)

response = requests.request("GET", url)

companies = []
response_list = response.json()
for item in response_list:
    companies.append(item['symbol'])

database = r"pythonsqlite.db"
conn = create_connection(database)

for company in set(companies):
    url = "https://financialmodelingprep.com/api/v3/profile/{}?apikey={}".format(company, fmp_api_key_ivan)
    response = requests.request("GET", url)
    response_text = response.json()[0]

    if response_text['isin'] is not None:
        row = (
            response_text['isin'],
            company,
            response_text['companyName'],
            response_text['price'],
            response_text['mktCap'],
            response_text['ipoDate'],
            generate_ts().strftime("%Y-%m-%d, %H:%M:%S")
        )

        insert_one_row(conn, row, table='company_profile')


