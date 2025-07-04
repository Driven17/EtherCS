import requests

import logging

from app_config import Config

STEAM_API_KEY = Config.STEAM_API_KEY

### STEAM RELATED ###
def fetch_steam_info(steam_id):
      
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    parameters = {
        "key": STEAM_API_KEY,
        "steamids": steam_id
    }

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:

        try:
            response = requests.get(url, params=parameters, timeout=5)
            response.raise_for_status()  # Raises an exception for 4xx/5xx errors
            return response.json()
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            logging.error(f"Steam API request failed: {e}, Attempt {attempts}")

    return None

def fetch_inventory(steam_id):

    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:

        try:
            inventory = requests.get(url, timeout=5)
            inventory.raise_for_status()
            logging.info(f"Inventory data for SteamID: {steam_id} fetched")
            return inventory.json()
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            logging.error(f"Steam API request failed: {e}, Attempt {attempts}")
    
    return None

### STEAM TRADE RELATED ###

def fetch_trade_info(access_token, tradeofferid):
      
    url = "https://api.steampowered.com/IEconService/GetTradeOffer/v1/"
    parameters = {
        "access_token": access_token,
        "tradeofferid": tradeofferid
    }

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:

        try:
            response = requests.get(url, params=parameters, timeout=5)
            response.raise_for_status()  # Raises an exception for 4xx/5xx errors
            return response.json()
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            logging.error(f"Steam API request failed: {e}, Attempt {attempts}")

    return None

def fetch_sent_trades(access_token):
      
    url = "https://api.steampowered.com/IEconService/GetTradeOffers/v1/"
    parameters = {
        "access_token": access_token,
        "get_sent_offers": True,
    }

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:

        try:
            response = requests.get(url, params=parameters, timeout=5)
            response.raise_for_status()  # Raises an exception for 4xx/5xx errors
            return response.json()
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            logging.error(f"Steam API request failed: {e}, Attempt {attempts}")

    return None
    
### WEB3 RELATED ###
def fetch_pol_usd():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'matic-network',
        'vs_currencies': 'usd'
    }

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            logging.info("MATIC/USD rate fetched")
            return data.get('matic-network', {}).get('usd')
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            logging.error(f"Request failed: {e}, Attempt {attempts}")
    
    return None

### EXTRA // MISC ###
def bymykel_json_fetch():
    url = f"https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/all.json"
    
    try:
        assets = requests.get(url, timeout=30)
        assets.raise_for_status()
        logging.info("All assets fetched - ByMykel's JSON.")
        return assets.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"ByMykel's JSON - Request failed: {e}")
    
    return None
