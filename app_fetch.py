import requests
from app_config import Config

STEAM_API_KEY = Config.STEAM_API_KEY

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
            print("Data successfully fetched!")
            return response.json()
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            print(f"Steam API request failed: {e}, Attempt {attempts}")

    return None

def fetch_inventory(steam_id):

    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:

        try:
            inventory = requests.get(url, timeout=5)
            inventory.raise_for_status()
            print("Data successfully fetched!")
            return inventory.json()
        
        except requests.exceptions.RequestException as e:
            attempts += 1
            print(f"Steam API request failed: {e}, Attempt {attempts}")
    
    return None

def parse_inventory(raw_inventory):
    if not raw_inventory:
        return None

    assets = raw_inventory.get('assets', [])
    descriptions = raw_inventory.get('descriptions', [])

    if not assets:
        return None
        
    desc_lookup = {
        (desc['classid'], desc['instanceid']): desc
        for desc in descriptions
    }

    inventory = []
    for asset in assets:
        key = (asset['classid'], asset['instanceid'])
        description = desc_lookup.get(key)

        if not description:
            continue

        inventory.append({
            'name': description.get('name'),
            'market_name': description.get('market_hash_name'),
            'tradable': description.get('tradable'),
            'inspect_link': description.get("actions", [])[0].get("link") if description.get("actions") else None,
            'icon_url': f"https://community.cloudflare.steamstatic.com/economy/image/{description.get('icon_url')}",
            
            'assetid': asset['assetid'],
            'classid': asset['classid'],
            'instanceid': asset['instanceid'],
        })
    return inventory

### EXTRA // MISC ###
def bymykel_json_fetch():
    url = f"https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/all.json"
    
    try:
        assets = requests.get(url, timeout=30)
        assets.raise_for_status()
        print("All assets successfully fetched! ByMykel's JSON.")
        return assets.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    return None
