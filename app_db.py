from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import BIGINT
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    steam_id = db.Column(BIGINT(unsigned=True), unique=True, nullable=False)
    display_name = db.Column(db.String(32), nullable=False)
    avatar = db.Column(db.Text, nullable=False)
    trade_url = db.Column(db.Text, nullable=True)
    steam_api_key = db.Column(db.Text, nullable=True)
    profile_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now(), nullable=False)

class Listing(db.Model):
    __tablename__ = "listings"

    listing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    market_name = db.Column(db.Text, nullable=False)
    asset_id = db.Column(BIGINT(unsigned=True), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    icon_url = db.Column(db.Text, nullable=False)
    listing_date = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)

### ALL FUNCTIONS // QUERIES ###

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
    listing = Listing.query.filter_by(asset_id=assetId, seller_id=sellerId).first()
    if listing:
        return listing
    return None

def user_listings(sellerId):
    listings = Listing.query.filter_by(seller_id=sellerId).all()
    if listings:
        return listings
    return None