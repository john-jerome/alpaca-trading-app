import configparser
import requests
import os

config = configparser.ConfigParser()
config.read('config.ini')

chat_id = config['telegram_bot']['chat_id']

api_key = os.environ['TELEGRAM_API_TOKEN']
endpoint = config['telegram_bot']['endpoint']

url = "{}{}/sendMessage".format(endpoint, api_key)

def send_state(action):
    """Send a state update message to Telegram

    Args:
        action (str): "started", "stopped" or "manually stopped"
    """
    message = ""
    if action == "started":
        message = "<b>Alpaca</b>: Program started"
    elif action == "stopped":
        message = "<b>Alpaca</b>: Program stopped unexpectedly"
    elif action == "manually stopped":
        message = "<b>Alpaca</b>: Program stopped manually"

    params = {
        'chat_id': chat_id, 
        'text': message, 
        'parse_mode': 'HTML'
    }

    requests.request("POST", url, params=params)

    return None

def send_order_message(
    account, action, order_class, symbol = None, 
    order_type = None, side = None,
    price = None, quantity = None
    ):

    if order_class == 'bracket':
        message = "<b>Alpaca</b> <b>{}:</b> We have created a <b>{} {}</b> order for <b>{}</b>".format(account.upper(), order_type, order_class, symbol)
    
    params = {
        'chat_id': chat_id, 
        'text': message, 
        'parse_mode': 'HTML'
    }

    requests.request("POST", url, params=params)

    return None
