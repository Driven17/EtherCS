import re
import requests

from urllib.parse import urlparse, parse_qs

def validate_trade_url(trade_url, steam_id):
    """
    Verify the trade URL belongs to the user's SteamID64.
    Returns (is_valid, token)
    """
    pattern = r"https://steamcommunity\.com/tradeoffer/new/\?partner=(\d+)&token=([a-zA-Z0-9]+)"
    match = re.match(pattern, trade_url)
    
    if not match:
        return False, None
    
    partner_id, token = match.groups()
    
    # Verify partner_id matches the user's SteamID32
    expected_partner_id = str(int(steam_id) - 76561197960265728)
    
    return partner_id == expected_partner_id, token

def parse_trade_link(trade_link):

    query = urlparse(trade_link).query
    params = parse_qs(query)
    
    partner = params.get('partner', [None])[0]
    token = params.get('token', [None])[0]

    return partner, token

def parse_and_sort_inventory(raw_inventory):
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
            
            'assetid': asset['assetid']
        })

    
    return inventory
