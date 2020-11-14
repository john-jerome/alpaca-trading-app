import configparser
import requests

config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['telegram_bot']['api_token']
chat_id = config['telegram_bot']['chat_id']

endpoint = config['telegram_bot']['endpoint']

def send_state(action):
    """[summary]

    Args:
        action ([string]): "started", "stopped" or "manually stopped"

    Returns:
        None
    """
    message = ""
    if action == "started":
        message = "Program started"
    elif action == "stopped":
        message = "Program stopped unexpectedly"
    elif action == "manually stopped":
        message = "Program stopped manually"

    url = "{}{}/sendMessage".format(endpoint, api_key)
    params = {
        'chat_id': chat_id, 
        'text': message, 
        'parse_mode': 'HTML'
    }

    requests.request("POST", url, params=params)

    return None

def send_message(action, account, instrument = None, order_type = None, side = None,\
     time = None, valid_until = None, price = None, quantity = None, order_uuid = None):
    """[summary]

    Args:
        action ([type]): [description]
        instrument ([type], optional): [description]. Defaults to None.
        order_type ([type], optional): [description]. Defaults to None.
        side ([type], optional): [description]. Defaults to None.
        valid_until ([type], optional): [description]. Defaults to None.
        price ([type], optional): [description]. Defaults to None.
        quantity ([type], optional): [description]. Defaults to None.
        order_uuid ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    url = "{}{}/sendMessage".format(endpoint, api_key)

    if action == 'create':
        if order_type == 'limit':
            message = "<b>{}</b>: We have <b>{}d</b> a {} <b>{}</b> order for <b>{}</b>: {} share(s) at <b>{}</b>€ at {}. It's valid until {}."\
                .format(account.upper(), action, order_type, side, instrument, quantity, round(float(price),2), time, valid_until)
        elif order_type == 'market':
            message = "<b>{}</b>: We have <b>{}d</b> a {} <b>{}</b> order for <b>{}</b>: {} share(s) at the market price at {}. It's valid until {}."\
                .format(account.upper(), action, order_type, side, instrument, quantity, time, valid_until)
    elif action == 'execute':
        message = "<b>{}</b>: We have <b>{}d</b> a {} <b>{}</b> order for <b>{}</b>: {} share(s) at <b>{}</b>€ at {}."\
            .format(account.upper(), action, order_type, side, instrument, quantity, price, time)

    params = {
        'chat_id': chat_id, 
        'text': message, 
        'parse_mode': 'HTML'
    }

    requests.request("POST", url, params=params)

    return None
