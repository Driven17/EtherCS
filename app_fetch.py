import requests
from app_config import Config

STEAM_API_KEY = Config.STEAM_API_KEY

def fetch_steam_user_info(steamId):
<<<<<<< HEAD
    
=======
      
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    parameters = {
        "key": STEAM_API_KEY,
        "steamids": steamId
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

def fetch_cs_inventory(steamId):

    url = f"https://steamcommunity.com/inventory/{steamId}/730/2"

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
<<<<<<< HEAD
        
        tags = description.get('tags', [])
        quality = next((tag['localized_tag_name'] for tag in tags if tag.get('category') == 'Rarity'), None)
        exterior = next((tag['localized_tag_name'] for tag in tags if tag.get('category') == 'Exterior'), None)
        type = next((tag['localized_tag_name'] for tag in tags if tag.get('category') == 'Type'), None)
        
        count = 0
        for tag in tags:
            if tag.get('category') == 'Quality':
                count += 1
        if count > 2:
            category = '★ StatTrak™'
        else:
            category = next((tag['localized_tag_name'] for tag in tags if tag.get('category') == 'Quality'), None)

        inventory.append({
            'name': description.get('name'),
            'market_hash_name': description.get('market_hash_name'),
            'type': type,
            'exterior': exterior,
            'quality': quality,
            'category': category,
            'tradable': description.get('tradable'),
            'inspect_link': description.get("actions", [])[0].get("link") if description.get("actions") else None,
            'icon_url': f"https://community.cloudflare.steamstatic.com/economy/image/{description.get('icon_url')}",
=======

        inventory.append({
            'name': description.get('name'),
            'market_name': description.get('market_hash_name'),
            'tradable': description.get('tradable'),
            'inspect_link': description.get("actions", [])[0].get("link") if description.get("actions") else None,
            'icon_url': f"https://community.cloudflare.steamstatic.com/economy/image/{description.get('icon_url')}",
            
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
            'assetid': asset['assetid'],
            'classid': asset['classid'],
            'instanceid': asset['instanceid'],
        })
<<<<<<< HEAD

    return inventory
=======
    return inventory

### EXTRA // MISC ###
def bymykel_json_fetch():
    url = f"https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/all.json"
    
    try:
        all_assets = requests.get(url, timeout=30)
        all_assets.raise_for_status()
        print("All assets successfully fetched! ByMykel's JSON.")
        return all_assets.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    return None
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
