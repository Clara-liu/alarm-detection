import requests
import yaml
import logging
import sys


def text_telegram(file):
    """Text with a telegram bot

    :param file: path to yaml file containing info on bot token and chat ID 
    :type file: str
    """
    with open(file, 'r') as f:
        try:
            cfg = yaml.safe_load(f)
        except yaml.YAMLError as e:
            sys.exit('Cannot load yaml file due to {e}')
    url = f"https://api.telegram.org/bot{cfg['token']}/sendMessage?chat_id={cfg['chat_id']}&text={'Alarm detected!'}"
    result = requests.get(url).json()
    if not result['ok']:
        logging.info('Alarm detected but cannot send telegram text!')
