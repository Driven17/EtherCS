from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.dialects.mysql import BIGINT

import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    steam_id = db.Column(BIGINT(unsigned=True), unique=True, index=True, nullable=False)

    display_name = db.Column(db.String(32), nullable=False)
    avatar = db.Column(db.Text, nullable=False)
    profile_url = db.Column(db.Text, nullable=False)

    trade_link = db.Column(db.LargeBinary, nullable=True) # Encrypted
    steam_api_key = db.Column(db.LargeBinary, nullable=True) # Encrypted
    wallet_address = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC), nullable=False)

class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

    assetid = db.Column(BIGINT(unsigned=True), nullable=False)

    price = db.Column(db.Numeric(10, 2), nullable=False)
    icon_url = db.Column(db.Text, nullable=False)
    inspect_link = db.Column(db.Text, nullable=True)

    status = db.Column(Enum(
        'Active', 'Inactive', 'Locked',
        'Sold', 'Removed', name='status'),
        default='Active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

    asset = db.relationship('Asset', backref='listings')

class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, index=True, nullable=False)
    type = db.Column(Enum
        ('Skin', 'Case', 'Sticker', 'Agent', 'Music Kit', 'Tool', 'Patch', 'Graffiti', 'Pass', 'Collectible', 'Charm', 'Gift', 'Key', 'Highlight', name='type'),
        nullable=False)
    category = db.Column(Enum
        ('Normal', 'Souvenir', 'StatTrak', 'Star','StarStatTrak', name='category'),
        default='Normal', nullable=False)

    quality = db.Column(db.String(32), nullable=True)
    color = db.Column(db.String(8), nullable = True)
    weapon_type = db.Column(db.String(64), nullable=True)
    skin = db.Column(db.String(64), nullable=True)
    exterior = db.Column(
        Enum('Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn','Battle-Scarred', 'Not Painted', name='exterior'),
        nullable=True)
    collection = db.Column(db.String(128), default=None, nullable=True)
    team = db.Column(
        Enum('Counter-Terrorist', 'Terrorist', 'Both Teams', name='team'),
        default=None, nullable=True)
    
    min_float = db.Column(db.Numeric(3,2), nullable=True)
    max_float = db.Column(db.Numeric(3,2), nullable=True)

    sticker_capsule = db.Column(db.String(128), nullable=True)
    sticker_effect = db.Column(db.String(16), nullable=True, default=None)
    sticker_type = db.Column(db.String(64), nullable=True)
    sticker_event = db.Column(db.String(64), nullable=True)
    sticker_team = db.Column(db.String(64), nullable=True)
    sticker_player = db.Column(db.String(64), nullable=True)

    icon_url = db.Column(db.String(512), nullable=False)

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Will be set to uniqueand indexed when web3 is integrated
    transaction_hash = db.Column(db.String(66), nullable=False)

    status = db.Column(Enum(
        'PendingAcceptance',
        'AwaitingSellerAction',
        'TradeSent',
        'Success',
        'Failed',
        name='transaction_status'
    ), default='PendingAcceptance', nullable=False)
    trade_offer_id = db.Column(BIGINT(unsigned=True), unique=True, index=True, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)

class Notification(db.Model):
    __tablename__ = "notifications"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
