import requests
import datetime
import os

import pandas as pd

import sendgrid
from sendgrid.helpers.mail import *

from twilio.rest import Client

DEX_URL = "https://api.dexscreener.io/latest/dex/search?q="
TIME = datetime.datetime.now()
EMAIL = 'najeeb.y@outlook.com'

TO_PHONE_NUMBER = '+4407979128641'

SERVER = 'smtp.sendgrid.net'
PORT = 587
USER = 'apikey'
PASSWORD = os.environ.get('SENDGRID_API_KEY')

tokens_url = '/Users/najeeb/Desktop/crypto/tokens.csv'

def main(up_multiplier=2.0, down_multiplier=0.75):
    prices = {}
    send_alerts = {}
    tokens = pd.read_csv(tokens_url)
    current_prices = get_current_prices(tokens)

    for token_id in current_prices.keys():
        prices[token_id] = (tokens[tokens['token'] == token_id]['last_checked'].iloc[0], current_prices[token_id][0])
        mask = tokens['token'] == token_id
        send_alerts[token_id] = 't' if tokens[mask]['notifications'].iloc[0] == 't' else 'f'

    diff = get_diff(prices, up_multiplier, down_multiplier)
    for token_id in diff.keys():
        if (True in diff[token_id]) and send_alerts[token_id]:
            direction = ''
            if diff[token_id][0]: direction = 'UP'
            if diff[token_id][1]: direction = 'DOWN'

            send_text(f""" \n
                Token: {current_prices[token_id][1]} with id {token_id} \n Has GONE {direction} to {prices[token_id][1]} from {prices[token_id][0]}
                  ({(prices[token_id][1]-prices[token_id][0])/ prices[token_id][0] * 100}%) last checked at {TIME}
                """)

            update_last_checked(token_id,prices[token_id][1], tokens_url)
    


def get_current_prices(tokens: pd.DataFrame, server_url=DEX_URL) -> dict[str, tuple[float, str]]:
    prices = {}
    for token_id in tokens['token']:
        url = server_url + token_id
        response = requests.get(url)
        if response.status_code == 200 and len(response.json().get('pairs')) > 0:
            try:
                price = response.json().get('pairs')[0].get('priceUsd')
                token_name = response.json().get('pairs')[0]['baseToken']['name']
            except ValueError:
                log_message('{}: Problem with API, probable schema change, token_id: {}, token name: {}. '.format(TIME, token_id, token_name))
            if price is not None:
                prices[token_id] =  (float(price), token_name)
            else:
                log_message('{}: Price not found, token_id: {}, token name: {}. '.format(TIME, token_id, token_name))
                raise ValueError('{}: Price not found, token_id: {}, token name: {}. Error logged at logs.txt'.format(TIME, token_id, token_name))
        else:
            log_message('{}: Error with endpoint, token_id: {}'.format(TIME, token_id))
            raise ValueError('Error with endpoint, token_id: {}. Error logged at logs.txt'.format(token_id))
    return prices


def get_diff(prices: dict[str, tuple[float, float]], up_multiplier, down_multiplier) -> dict[str, bool]:
    """
    Input
        - prices = {token_id: (price_purchased, current_price)}
        - multiplier = 2.0

    Output
        - {token_id: bool}
    
    If check_type is 'profit' then the value will be True if the current price is greater than the price purchased * multiplier
    and the value will be False otherwise

    If check_type is 'loss' then the value will be True if the current price is less than the price purchased * multiplier
    and the value will be False otherwise
    """
    diff = {}
    for token_id in prices.keys():
        profit = prices[token_id][1] >= prices[token_id][0] * up_multiplier
        loss = prices[token_id][1] < prices[token_id][0] * down_multiplier
        diff[token_id] = (profit,loss)
    return diff    

    



def send_email(message):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email='najeeb.y@outlook.com'
    to_email=EMAIL
    subject='Profit Checker'
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, to_email, subject, content)
    mail_json = mail.get()
    response = sg.client.mail.send.post(request_body=mail_json)
    return




def send_text(text):

    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)
        message = client.messages \
                    .create(
                        body=text,
                        from_='+12183199285',
                        to=TO_PHONE_NUMBER
                    )

        log_message(f"Message: {text} sent. Time: {TIME}. Message ID: {message.sid}") 

    except ValueError:
        print('Twilio authentication credentials not found, please ensure the environment variables `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` are accessible by the script')

    

            
# UTILS 
def log_message(txt, filepath='logs.txt'):
    with open(filepath, 'a') as f:
        f.write(txt + '\n')
  

def update_token_alerts(token_id:str, filepath='tokens.csv') -> None:
    try:
        df = pd.read_csv(filepath, index_col=0)
        df = df.reset_index(drop=True)
        alert_status = 'f' if df[df['token'] == token_id]['notifications'] == 't' else 't'
        token_mask = df['token'].srt.startswith(token_id)
        df.loc[token_mask, 'notifications'] = alert_status
        df.to_csv(filepath, index=False)
                
    except FileNotFoundError:
        print("File not found")
        log_message(f'{TIME}: Tokens file not found')

    except IndexError:
        print(f"Error accessing index in '{filepath}' file")
        log_message(f"{TIME}: Error accessing index in '{filepath}' file")


def update_last_checked(token_id:str, current_price:float, filepath='tokens.csv') -> None:
    df = pd.read_csv(filepath)
    token_mask = df['token'].str.startswith(token_id)
    df.loc[token_mask, 'last_checked'] = current_price
    df.to_csv(filepath, index=False)
                
if __name__ == "__main__":
    main()


    #* * * * * /Library/Frameworks/Python.framework/Versions/3.12/bin/python3  /Users/najeeb/Desktop/crypto/hello_world.py  >> /Users/najeeb/Desktop/crypto/testing_cron.txt 2>&1