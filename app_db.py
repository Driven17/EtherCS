from models import db, User, Asset, Listing
from sqlalchemy import func
import datetime

### ALL FUNCTIONS // QUERIES ###

# USER RELATED
def is_user(steam_id):
    user = (User
            .query
            .filter_by(steam_id=steam_id)
            .first())
    return bool(user)

def get_user_by_steam_id(steam_id):
    return (User
            .query
            .filter_by(steam_id=steam_id)
            .first())

def get_user_by_user_id(user_id):
    return (User
            .query
            .filter_by(id=user_id)
            .first())
    
def update_last_login(user_id):
    # Triggers SQLAlchemy's `onupdate` for `last_login` without modifying any actual field.
    # This relies on `onupdate=datetime.datetime.now()` in the model definition.
    (db.session
     .query(User)
     .filter_by(id=user_id)
     .update({}))
    db.session.commit()
    print(f"User ({user_id}) logged in at {datetime.datetime.now()}")

def create_user(steam_data):
    # Validates steam data and stores it in DB 
    if steam_data:
        steam_data = steam_data["response"]["players"][0]
        new_user = User(
            steam_id = steam_data["steamid"],
            display_name = steam_data["personaname"],
            avatar = steam_data["avatar"],
            profile_url = steam_data["profileurl"]
        )
        db.session.add(new_user)
        db.session.commit()
        print("New user successfully saved.")
        return True
    return None

# LISTING RELATED
def create_listing(seller_id, asset_id, assetid, classid, instanceid, price, icon_url, inspect_link):
    # Use existing function to check if item is already listed.
    if is_listing(assetid, seller_id):
        print("Item is already listed.")
        return False
    
    new_listing = Listing(
        seller_id = seller_id,
        asset_id = asset_id,
        assetid = assetid,
        classid = classid,
        instanceid = instanceid,
        price = price,
        icon_url = icon_url,
        inspect_link = inspect_link
    )
    db.session.add(new_listing)
    db.session.commit()
    print("New listing successfully saved.")
    return True

def delete_listing(listing_id):
    listing = (Listing
                    .query
                    .filter_by(id=listing_id).first())
    if listing:
        db.session.delete(listing)
        db.session.commit()
        print(F"Listing {listing_id} successfully deleted.")
        return True
    return False
    
def update_price(listing_id, new_price):
    listing = (Listing
               .query
               .filter_by(id=listing_id)
               .first())
    if listing:
        old_price = listing.price
        listing.price = float(new_price)
        db.session.commit()
        print(f"Listing ID: {listing_id} - Price successfully changed from ${old_price} to ${new_price}")
        return True
    return None
    
def is_listing(assetid, seller_id):
    listing = (Listing
               .query
               .filter_by(assetid=assetid, seller_id=seller_id)
               .first())
    return bool(listing)

def build_listings_by_seller(seller_id):
    if not seller_id:
        return None
    
    listings = (Listing
                .query
                .filter_by(seller_id=seller_id)
                .all())
    
    if listings:
        return [
            {
                'id': listing.id,
                'seller_id': listing.seller_id,
                'price': listing.price,
                'icon_url': listing.icon_url,
                'inspect_link': listing.inspect_link,
                'market_name': listing.asset.name,
                'weapon_type': listing.asset.weapon_type,
                'exterior': listing.asset.exterior
            }
            for listing in listings
        ]
    return None

# MARKET RELATED
def build_marketplace_data():
    assets = (
        db.session.query(
            Listing.asset_id,
            Asset.name,
            Asset.icon_url.label('icon'),
            func.count(Listing.id).label('total_listings'),
            func.min(Listing.price).label('min_price')
        )
        .join(Asset, Listing.asset_id == Asset.id)
        .group_by(Listing.asset_id, Asset.name, Asset.icon_url)
        .order_by(func.min(Listing.price).asc())
        .all()
    )
    return [
        {
            'id': asset.asset_id,
            'market_name': asset.name,
            'icon': asset.icon,
            'total_listings': asset.total_listings,
            'min_price': asset.min_price
        }
        for asset in assets
    ]

def get_listings_by_asset(asset_id):
    return (
        Listing.query
        .filter_by(asset_id=asset_id)
        .order_by(Listing.price.asc())
        .all()
    )

def get_asset_data_by_name(market_name):
    asset = (Asset
             .query
             .filter_by(name=market_name)
             .first())
    return asset

def get_asset_data_by_id(asset_id):
    asset = (Asset
             .query
             .filter_by(id=asset_id)
             .first())
    return asset

# SCRIPTS // MISC
def bymykel_json_db(
    name, type, category, quality, color,
    weaponType, skin, exterior, collection, 
    team, min_float, max_float, sticker_capsule,
    sticker_effect, sticker_event, stickerType,
    sticker_team, sticker_player, icon_url, asset_number, total_length):

    """This is a script to store everything into the static table 'assets' in the database."""
    new_asset = Asset(
        name = name,
        type = type,
        category = category,
        quality = quality,
        color = color,
        weapon_type = weaponType,
        skin = skin,
        exterior = exterior,
        collection = collection,
        team = team,
        min_float = min_float,
        max_float = max_float,
        sticker_capsule = sticker_capsule,
        sticker_effect = sticker_effect,
        sticker_type = stickerType,
        sticker_event = sticker_event,
        sticker_team = sticker_team,
        sticker_player = sticker_player,
        icon_url = icon_url
    )
    db.session.add(new_asset)
    db.session.commit()
    print(f"Success {int(asset_number/total_length*100)}%")

def bymykel_asset_exists(name):
    asset_name = (Asset
                  .query
                  .filter_by(name=name)
                  .first())
    if asset_name:
        return True
    return False
