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

    trade_url = db.Column(db.Text, nullable=True)
    steam_api_key = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now(), nullable=False)

class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)

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
    type = db.Column(Enum
        ('Skin', 'Case', 'Sticker', 'Agent', 'Music Kit', 'Tool', 'Patch', 'Graffiti', 'Pass', 'Collectible', 'Charm', 'Gift', 'Key', name='type'),
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
