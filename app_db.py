from app_models import db, User, Asset, Listing, Transaction, Notification
from app_encryption import decrypt
from app_steam import parse_trade_link

from sqlalchemy import func

from datetime import timedelta
import datetime

import logging

### ALL FUNCTIONS // QUERIES ###

# === USER RELATED ===
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
    logging.info(f"UserID: {user_id} - Logged in at {datetime.datetime.now(datetime.UTC)}")

def create_user(steam_data):
    # Validates steam data and stores it in DB 
    if not steam_data:
        return None
    steam_data = steam_data["response"]["players"][0]

    steam_id = steam_data["steamid"]

    new_user = User(
        steam_id = steam_id,
        display_name = steam_data["personaname"],
        avatar = steam_data["avatar"],
        profile_url = steam_data["profileurl"]
    )
    db.session.add(new_user)
    db.session.commit()
    logging.info(f"New user added - SteamID64: {steam_id}")
    return True

# === LISTING RELATED ===
def insert_listing(seller_id, asset_id, assetid, price, icon_url, inspect_link):
    
    new_listing = Listing(
        seller_id = seller_id,
        asset_id = asset_id,
        assetid = assetid,
        price = price,
        icon_url = icon_url,
        inspect_link = inspect_link
    )
    db.session.add(new_listing)
    db.session.commit()
    logging.info(f"New listing added by UserID: {seller_id}")
    return True

def delete_listing(listing_id):
    listing = (Listing
                    .query
                    .filter_by(id=listing_id).first())
    if listing:
        db.session.delete(listing)
        db.session.commit()
        logging.info(f"Deleted ListingID: {listing_id}")
        return True
    return False
    
def update_listing_price(listing_id, new_price):
    listing = (Listing
               .query
               .filter_by(id=listing_id)
               .first())
    
    if not listing:
        return None
    
    old_price = listing.price
    listing.price = float(new_price)
    db.session.commit()
    logging.info(f"ListingID: {listing_id} - Price changed from ${old_price} to ${new_price}")
    return True

def is_listing(assetid, seller_id):
    listing = (Listing
               .query
               .filter(Listing.assetid == assetid, Listing.seller_id == seller_id)
               .filter(Listing.status != 'Removed')
               .filter(Listing.status != 'Sold')
               .first())
    return bool(listing)

def get_listing_by_id(listing_id):
    return (Listing
            .query
            .filter_by(id=listing_id)
            .first())

def build_listings_by_seller(seller_id):
    if not seller_id:
        return None
    
    listings = (Listing
                .query
                .filter_by(
                    seller_id=seller_id,
                    status='Active'
                           )
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

def edit_listing_status(listing_id, new_status):
    if new_status not in ['Active', 'Inactive', 'Locked', 'Sold', 'Removed']:
        return False
    
    if not listing_id:
        return False
    
    listing = get_listing_by_id(listing_id)
    old_status = listing.status
    listing.status = new_status
    logging.info(f"ListingID: {listing_id} - Status changed from {old_status} to {new_status}")
    return True

# === MARKET RELATED ===
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
        .filter(Listing.status == 'Active')
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
        .filter_by(
            asset_id=asset_id,
            status='Active'
            )
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

# === TRANSACTION RELATED ===
def create_transaction(buyer_id, seller_id, listing_id, amount, transaction_hash):
    new_transaction = Transaction(
        buyer_id=buyer_id,
        seller_id=seller_id,
        listing_id=listing_id,
        amount=amount,
        transaction_hash=transaction_hash,
    )
    logging.info(f"New transaction initiated between BuyerID: {buyer_id} & SellerID: {seller_id}")
    db.session.add(new_transaction)
    db.session.commit()
    return True

def edit_transaction_status(transaction_id, new_status):
    valid_statuses = [
        'PendingAcceptance',
        'AwaitingSellerAction',
        'TradeSent',
        'Success',
        'Failed'
    ]

    if new_status not in valid_statuses:
        return False
    
    transaction = (Transaction
                   .query
                   .filter_by(id=transaction_id)
                   .first())
    
    old_status = transaction.status
    transaction.status = new_status # Set new status

    db.session.commit()
    logging.info(f"TransactionID: {transaction_id} - Status changed from {old_status} to {new_status}")
    return True

def get_buyer_and_seller(transaction_id):
    transaction = (Transaction
                   .query
                   .get_or_404(transaction_id))
    
    if not transaction_id:
        return False
    
    return {
        "buyer_id": transaction.buyer_id,
        "seller_id": transaction.seller_id
    }

def get_sales_by_user_id(user_id):
    sales = (
        db.session.query(
            Transaction.id.label('transaction_id'),
            Transaction.amount,
            Transaction.status,
            Transaction.created_at,
            Listing.icon_url,
            Listing.inspect_link,
            Asset.name.label('market_name'),
            User.display_name.label('buyer_name'),
            User.profile_url.label('buyer_profile'),
            User.trade_link.label('buyer_trade_link')
        )
        .join(Listing, Transaction.listing_id == Listing.id)
        .join(Asset, Listing.asset_id == Asset.id)
        .join(User, Transaction.buyer_id == User.id)
        .filter(Transaction.seller_id == user_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return [
        {
            'transaction_id': t.transaction_id,
            'amount': t.amount,
            'status': t.status,
            'created_at': t.created_at,
            'icon_url': t.icon_url,
            'inspect_link': t.inspect_link,
            'market_name': t.market_name,
            'buyer_name': t.buyer_name,
            'buyer_profile': t.buyer_profile,
            'buyer_trade_link': decrypt(t.buyer_trade_link) if t.status == 'Pending' else None
        }
        for t in sales
    ]

def get_purchases_by_user_id(user_id):

    purchases = (
        db.session.query(
            Transaction.id.label('transaction_id'),
            Transaction.amount,
            Transaction.status,
            Transaction.created_at,
            Listing.icon_url,
            Listing.inspect_link,
            Asset.name.label('market_name'),
            User.display_name.label('seller_name'),
            User.profile_url.label('seller_profile'),
            Transaction.trade_offer_id
        )
        .join(Listing, Transaction.listing_id == Listing.id)
        .join(Asset, Listing.asset_id == Asset.id)
        .join(User, Transaction.seller_id == User.id)
        .filter(Transaction.buyer_id == user_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return [
        {
            'transaction_id': t.transaction_id,
            'amount': t.amount,
            'status': t.status,
            'created_at': t.created_at,
            'icon_url': t.icon_url,
            'inspect_link': t.inspect_link,
            'market_name': t.market_name,
            'seller_name': t.seller_name,
            'seller_profile': t.seller_profile,
            'trade_offer_id': t.trade_offer_id
        }
        for t in purchases
    ]

def insert_trade_offer_id(transaction_id, new_trade_offer_id):
    transaction = (Transaction
                   .query
                   .get_or_404(transaction_id))
    
    transaction.trade_offer_id = new_trade_offer_id
    db.session.commit()

def get_pending_trades_by_user(user_id):
    trades = (
        Transaction.query
        .filter_by(seller_id=user_id)
        .filter(Transaction.status == 'TradeSent')
        .all()
    )
    return [{'offer_id': trade.trade_offer_id} for trade in trades]

def get_transaction_id_by_offer_id(offer_id):
    transaction = (Transaction.query
                   .filter_by(trade_offer_id=offer_id)
                   .first())
    if transaction:
        return transaction.id
    return None

def get_listing_id_by_transaction_id(transaction_id):
    return (Transaction
            .query
            .get_or_404(transaction_id)
            .listing_id)

# === USER NOTIFICATIONS ===
def create_notification(user_id, message):
    if not message:
        return False
    new_notification = Notification(
        user_id = user_id,
        message = message
    )
    db.session.add(new_notification)
    db.session.commit()
    logging.info(f"Notification sent to UserID: {user_id}")
    return True

def get_notifications(user_id):
    return (Notification
     .query
     .filter_by(user_id = user_id)
     .all())

def update_notification_as_read(notification_id):
    notification = (Notification
                    .query
                    .filter_by(id=notification_id)
                    .first())
    if not notification:
        return False
    notification.is_read = True
    db.session.commit()
    return True

# === PAYLOAD BUILDING / API POST BUILDING ===
def build_trade_payload(transaction_id):
    payload = (
        db.session.query(
            Listing.assetid,
            User.steam_id,
            User.trade_link,
            Transaction.id.label('transaction_id'),
        )
        .join(Transaction, Transaction.listing_id == Listing.id)
        .join(User, User.id == Transaction.buyer_id)
        .filter(Transaction.id == transaction_id)
        .first()
    )
    
    partner_id, trade_token = parse_trade_link(decrypt(payload.trade_link))

    return {
        "item_assetid": str(payload.assetid),
        "buyer_steam_id": str(payload.steam_id),
        "buyer_partner_id": str(partner_id),
        "buyer_trade_token": trade_token,
        "message": f"EtherCS - Transaction #{payload.transaction_id}"
    }

# === SETTINGS ===
def update_user_settings(user_id, setting, value):
    user = (User
            .query
            .filter_by(id=user_id)
            .first())
    if not user:
        return False

    if setting not in {"trade_link", "steam_api_key", "wallet_address", "trade_access_token"}:
        return False
    
    setattr(user, setting, value)
    try:
        db.session.commit()
        logging.info(f"UserID: {user_id} - Updated {setting}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"UserID: {user_id} - Failed to update {setting}: {e}")
        return False
    
# === SCRIPTS // MISC ===
def bymykel_json_db(
    name, type, category, quality, color,
    weapon_type, skin, exterior, collection, 
    team, min_float, max_float, sticker_capsule,
    sticker_effect, sticker_type, sticker_event,
    sticker_team, sticker_player, icon_url, asset_number, total_length):

    """This is a script to store everything into the static table 'assets' in the database."""
    new_asset = Asset(
        name = name,
        type = type,
        category = category,
        quality = quality,
        color = color,
        weapon_type = weapon_type,
        skin = skin,
        exterior = exterior,
        collection = collection,
        team = team,
        min_float = min_float,
        max_float = max_float,
        sticker_capsule = sticker_capsule,
        sticker_effect = sticker_effect,
        sticker_type = sticker_type,
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
