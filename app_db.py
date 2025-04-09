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
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now(), nullable=False)



### ALL FUNCTIONS // QUERIES ###

# Checks if user exists in DB by steam id
def user_exists(steam_id):
    user = User.query.filter_by(steam_id=steam_id).first()
    if user:
        return True

# Validates steam data and stores it in DB 
def store_new_user(steam_data):
    if steam_data:
        steam_data = steam_data["response"]["players"][0]
        new_user = User(
            steam_id = steam_data["steamid"],
            display_name = steam_data["personaname"],
            avatar = steam_data["avatar"]
        )
        db.session.add(new_user)
        db.session.commit()
        print("New user successfully saved.")
        return True
    
    else:
        return None