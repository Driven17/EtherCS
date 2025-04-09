import requests
from app_config import Config

STEAM_API_KEY = Config.STEAM_API_KEY

def fetch_steam_user_info(steam_id):
    
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    parameters = {
        "key": STEAM_API_KEY,
        "steamids": steam_id
    }

    max_attempts = 4
    attempts = 0

    while attempts < max_attempts:

        try:
            response = requests.get(url, params=parameters, timeout=5)
            response.raise_for_status()  # Raises an exception for 4xx/5xx errors
            print("Data successfully fetched!")
            return response.json()
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            print(f"Steam API request failed: {e}, Attempt {attempts}")

    return None