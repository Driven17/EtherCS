from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, Enum
from sqlalchemy.dialects.mysql import BIGINT
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    steam_id = db.Column(BIGINT(unsigned=True), unique=True, nullable=False)

    display_name = db.Column(db.String(32), nullable=False)
    avatar = db.Column(db.Text, nullable=False)
    profile_url = db.Column(db.Text, nullable=False)

    trade_url = db.Column(db.Text, nullable=True)
    steam_api_key = db.Column(db.Text, nullable=True)
<<<<<<< HEAD
    profile_url = db.Column(db.Text, nullable=False)
=======

>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now(), nullable=False)

class Listing(db.Model):
    __tablename__ = "listings"
<<<<<<< HEAD
=======

    listing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

    assetid = db.Column(BIGINT(unsigned=True), nullable=False)
    classid = db.Column(BIGINT(unsigned=True), nullable=False)
    instanceid = db.Column(BIGINT(unsigned=True), nullable=False)

    price = db.Column(db.Numeric(10, 2), nullable=False)
    icon_url = db.Column(db.Text, nullable=False)
    inspect_link = db.Column(db.Text, nullable=True)
    listing_date = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)

    asset = db.relationship('Asset', backref='listings')

class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, index=True, nullable=False)
    type = db.Column(
        Enum('Skin', 'Case', 'Sticker', 'Agent',
            'Music Kit', 'Tool', 'Patch', 'Graffiti', 'Pass', 'Collectible',
            'Charm', 'Gift', 'Key', name='type'), nullable=False)
    category = db.Column(
        Enum('Normal', 'Souvenir', 'StatTrak', 
             'Star','StarStatTrak', name='category'),
               default='Normal', nullable=False)
    quality = db.Column(db.String(32), nullable=True)
    color = db.Column(db.String(8), nullable = True)
    weapon_type = db.Column(db.String(64), nullable=True)
    skin = db.Column(db.String(64), nullable=True)
    exterior = db.Column(
        Enum('Factory New', 'Minimal Wear', 'Field-Tested', 
             'Well-Worn','Battle-Scarred', 'Not Painted', name='exterior'), nullable=True)
    collection = db.Column(db.String(128), nullable=True)
    team = db.Column(
        Enum('Counter-Terrorist', 'Terrorist', 
             'Both Teams', name='team'), default=None, nullable=True)
    
    min_float = db.Column(db.Numeric(3,2), nullable=True)
    max_float = db.Column(db.Numeric(3,2), nullable=True)

    sticker_capsule = db.Column(db.String(128), nullable=True)
    sticker_effect = db.Column(db.String(16), nullable=True, default=None)
    sticker_type = db.Column(db.String(64), nullable=True)
    sticker_event = db.Column(db.String(64), nullable=True)
    sticker_team = db.Column(db.String(64), nullable=True)
    sticker_player = db.Column(db.String(64), nullable=True)

    icon_url = db.Column(db.String(512), nullable=False)

>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)

    listing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    market_name = db.Column(db.Text, nullable=False)
    asset_id = db.Column(BIGINT(unsigned=True), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    icon_url = db.Column(db.Text, nullable=False)
    listing_date = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)

### ALL FUNCTIONS // QUERIES ###

<<<<<<< HEAD
=======
# USER RELATED
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
def user_exists(steamId):
    # Checks if user exists in DB by steam id
    user = User.query.filter_by(steam_id=steamId).first()
    if user:
        return True
    
def get_user_info(steamId):
    return User.query.filter_by(steam_id=steamId).first()
    
def update_last_login(userId):
    db.session.query(User).filter_by(user_id=userId).update({})
    db.session.commit()

def store_new_user(steamData):
    # Validates steam data and stores it in DB 
    if steamData:
        steamData = steamData["response"]["players"][0]
        new_user = User(
            steam_id = steamData["steamid"],
            display_name = steamData["personaname"],
            avatar = steamData["avatar"],
            profile_url = steamData["profileurl"]
        )
        db.session.add(new_user)
        db.session.commit()
        print("New user successfully saved.")
        return True
    return None

# LISTING RELATED
<<<<<<< HEAD
def create_listing(listingData):
    # Use existing function to check if item is already listed.
    if listing_exists(listingData.asset_id, listingData.seller_id):
        print("Item is already listed.")
        return None
    
    if listingData:
        new_listing = Listing(
            seller_id = listingData.seller_id,
            market_name = listingData.market_name,
            asset_id = listingData.asset_id,
            price = listingData.price,
            icon_url = listingData.icon_url
        )
        db.session.add(new_listing)
        db.session.commit()
        print("New listing successfully saved.")
        return True
=======
def create_listing(sellerId, marketId, assetid, classid, instanceid, price, iconUrl, inspectLink):
    # Use existing function to check if item is already listed.
    if listing_exists(assetid, sellerId):
        print("Item is already listed.")
        return None
    
    new_listing = Listing(
        seller_id = sellerId,
        market_id = marketId,
        assetid = assetid,
        classid = classid,
        instanceid = instanceid,
        price = price,
        icon_url = iconUrl,
        inspect_link = inspectLink
    )
    db.session.add(new_listing)
    db.session.commit()
    print("New listing successfully saved.")
    return True
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)

def delete_listing(listingId):
    if listingId:
        currentListing = Listing.query.filter_by(listing_id=listingId).first()
        db.session.delete(currentListing)
        db.session.commit()
        print(F"Listing {listingId} successfully deleted.")
        return True
    return None
    
def edit_price(listingId, newPrice):
    listing = Listing.query.filter_by(listing_id=listingId).first()
    if listing:
        old_price = listing.price
        listing.price = float(newPrice)
        db.session.commit()
        print(f"Listing ID: {listingId} - Price successfully changed from ${old_price} to ${newPrice}")
        return True
    return None
    
def listing_exists(assetId, sellerId):
<<<<<<< HEAD
    listing = Listing.query.filter_by(asset_id=assetId, seller_id=sellerId).first()
=======
    listing = Listing.query.filter_by(assetid=assetId, seller_id=sellerId).first()
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
    if listing:
        return listing
    return None

def user_listings(sellerId):
<<<<<<< HEAD
    listings = Listing.query.filter_by(seller_id=sellerId).all()
    if listings:
        return listings
    return None
=======
    if not sellerId:
        return None
    
    listings = Listing.query.filter_by(seller_id=sellerId).all()
    if listings:
        return [
            {
                'listing_id': l.listing_id,
                'seller_id': l.seller_id,
                'price': l.price,
                'icon_url': l.icon_url,
                'inspect_link': l.inspect_link,
                'market_name': l.asset.name,
                'weapon_type': l.asset.weapon_type,
                'exterior': l.asset.exterior
            }
            for l in listings
        ]
    return None

# MARKET RELATED
def marketplace_data():
    assets = (
        db.session.query(
            Listing.market_id,
            Asset.name,
            Asset.icon_url.label('icon'),
            func.count(Listing.listing_id).label('total_listings'),
            func.min(Listing.price).label('min_price')
        )
        .join(Asset, Listing.market_id == Asset.id)
        .group_by(Listing.market_id, Asset.name, Asset.icon_url)
        .order_by(func.min(Listing.price).asc())
        .all()
    )
    return [
        {
            'id': asset.market_id,
            'market_name': asset.name,
            'icon': asset.icon,
            'total_listings': asset.total_listings,
            'min_price': asset.min_price
        }
        for asset in assets
    ]

def get_listings(assetId):
    return (
        Listing.query
        .filter_by(market_id=assetId)
        .order_by(Listing.price.asc())
        .all()
    )

def get_asset_data_byname(marketName):
    asset = Asset.query.filter_by(name=marketName).first()
    if asset:
        return asset
    return None

def get_asset_data_byid(assetId):
    asset = Asset.query.filter_by(id=assetId).first()
    if asset:
        return asset
    return None

# SCRIPTS // MISC
def bymykel_json_db(name, type, category, quality, color,
                    weaponType, skin, exterior, collection, 
                    team, minFloat, maxFloat, stickerCapsule, stickerEffect, stickerEvent,
                    stickerType, stickerTeam, stickerPlayer, iconUrl, assetNo, totalLength):
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
        min_float = minFloat,
        max_float = maxFloat,
        sticker_capsule = stickerCapsule,
        sticker_effect = stickerEffect,
        sticker_type = stickerType,
        sticker_event = stickerEvent,
        sticker_team = stickerTeam,
        sticker_player = stickerPlayer,
        icon_url = iconUrl
    )
    db.session.add(new_asset)
    db.session.commit()
    print(f"Success {int(assetNo/totalLength*100)}%")

def bymykel_asset_exists(name):
    asset_name = Asset.query.filter_by(name=name).first()
    if asset_name:
        return True
    return False
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
