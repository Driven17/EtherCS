from flask import Flask, redirect, url_for, session, request, render_template
from flask_migrate import Migrate
from functools import wraps
from app_fetch import fetch_steam_info, fetch_inventory, parse_inventory
from app_config import Config
from models import db
from app_db import (
    is_user, update_last_login, create_user, get_user_by_user_id, get_user_by_steam_id, 
    create_listing, build_listings_by_seller, update_price, delete_listing,
    get_asset_data_by_name, get_asset_data_by_id, get_listings_by_asset, build_marketplace_data,
)
import requests

# Init steam openID url without parameters
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
BASE_URL = "http://192.168.86.85:3000"

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app) # Initialize DB
migrate = Migrate(app, db) # Initialize Flask-Migrates
with app.app_context():
    db.create_all()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Replace 'login' with your actual route name
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    user = get_user_by_user_id(session.get('user_id'))
    return render_template('home.html', user=user)

### USER DASHBOARD SECTIONS ###
@app.route("/inventory/")
@login_required
def inventory():
    user = get_user_by_user_id(session.get('user_id', None))
    steam_id = session.get('steam_id')
    #inventory = fetch_inventory('76561198045277210') #OHNE PIXEL INVENTORY ||| FOR TESTING |||
    inventory = parse_inventory(fetch_inventory(steam_id))
    
    return render_template('inventory.html', steam_id=steam_id, inventory=inventory, user=user)

@app.route("/inventory/list", methods=['POST'])
@login_required
def list_item():
    # VALIDATION START
    """Make sure that the user has that item with the same assetid, classid and instanceid in his inventory"""
    # VALIDATION END

    seller_id = session.get("user_id") # get user id (seller_id) on platform

    assetid = int(request.form['assetid'])
    classid = int(request.form['classid'])
    instanceid = int(request.form['instanceid'])

    market_name = str(request.form['market_name'])
    icon_url = request.form['icon_url']
    inspect_link = request.form['inspect_link']
    
    if inspect_link == 'None':
        inspect_link = None

    price = float(request.form['price'])

    ### LISTING ###
    asset_data = get_asset_data_by_name(market_name)
    if not asset_data:
        return "Invalid item"
    
    listing_created = create_listing(seller_id, asset_data.id, assetid, classid, instanceid, price, icon_url, inspect_link)
    if listing_created:
        return redirect(url_for("inventory"))
    
    return "Item already listed"

@app.route("/mylistings/")
@login_required
def mylistings():
    user = get_user_by_user_id(session.get('user_id'))
    listings = build_listings_by_seller(user.id)
    return render_template("mylistings.html", user=user, listings=listings)

@app.route("/mylistings/edit", methods=['POST'])
@login_required
def mylistings_edit():
    seller_id = int(request.form['seller_id'])

    # Validate that user in session is one editing the listing's price
    if session.get('user_id') == seller_id:

        listing_id = int(request.form['listing_id'])
        new_price = float(request.form['new_price'])

        update_price(listing_id, new_price)
        return redirect(url_for('mylistings'))
    return "Invalid"

@app.route("/mylistings/delete", methods=['POST'])
@login_required
def mylistings_delete():
    seller_id = int(request.form['seller_id'])

    # Validate that user in session is one deleting the listing
    if session.get('user_id') == seller_id: 
        listing_id = int(request.form['listing_id'])
        print(listing_id)
        delete_listing(listing_id)
        return redirect(url_for('mylistings'))
    return "Invalid"
### USER DASHBOARD SECTIONS ###

### MARKET START ###
@app.route("/market")
def market():
    user = get_user_by_user_id(session.get('user_id'))
    assets = build_marketplace_data()
    return render_template('market.html', user=user, assets=assets)

@app.route("/market/item/<int:asset_id>/")
def market_item(asset_id):
    user = get_user_by_user_id(session.get('user_id'))
    asset_data = get_asset_data_by_id(asset_id)
    listings = get_listings_by_asset(asset_id)
    return render_template('market_item.html', asset=asset_data, listings=listings, user=user)
### MARKET END ###

### LOGIN START ###
@app.route("/login")
def login():
    """Redirects users to Steam's OpenID login page"""
    return_to_url = f"{BASE_URL}/after_login"
    steam_login_url = (
        f"{STEAM_OPENID_URL}?"
        "openid.ns=http://specs.openid.net/auth/2.0&"
        "openid.mode=checkid_setup&"
        f"openid.return_to={return_to_url}&"
        f"openid.realm={BASE_URL}/&"
        "openid.identity=http://specs.openid.net/auth/2.0/identifier_select&"
        "openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
    )
    return redirect(steam_login_url)

@app.route("/after_login")
def after_login():
    if "openid.identity" not in request.args:
        return "Steam login failed", 400

    steam_id = request.args["openid.identity"].split("/")[-1] # Extract Steam ID from OpenID URL

    openid_params = {key: request.args[key] for key in request.args}
    openid_params["openid.mode"] = "check_authentication" # Verify OpenID response

    response = requests.post(STEAM_OPENID_URL, data=openid_params)
    if "is_valid:true" not in response.text:
        return "Steam login validation failed", 400

    session["steam_id"] = steam_id  # Store in session
    
    ### Checks if user is new or returning - If new, data is stored in DB ###

    if not is_user(steam_id):
        user_data = fetch_steam_info(steam_id)
        create_user(user_data)

    user = get_user_by_steam_id(steam_id)
    session["user_id"] = user.id
    update_last_login(user.id)

    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("home"))
### LOGIN END ###

### DEBUGGING ROUTE ###
@app.route("/debug")
def debug():
    return dict(session)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)