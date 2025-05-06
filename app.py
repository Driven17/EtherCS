from flask import Flask, redirect, url_for, session, request, render_template
from flask_migrate import Migrate
from app_fetch import fetch_steam_user_info, fetch_cs_inventory, parse_inventory
from app_config import Config
<<<<<<< HEAD
from app_db import db, user_exists, update_last_login, store_new_user, get_user_info, create_listing, user_listings, edit_price, delete_listing
from app_classes import Listing
=======
from app_db import (
    db, user_exists, update_last_login, store_new_user, get_user_info, 
    create_listing, user_listings, edit_price, delete_listing, marketplace_data,
    get_asset_data_byname, get_asset_data_byid, get_listings
)
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
import requests

# Init steam openID url without parameters
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
URL = "http://192.168.86.85:3000"

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app) # Initialize DB
migrate = Migrate(app, db) # Initialize Flask-Migrates
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    steam_id = session.get("steam_id")
    user = get_user_info(steam_id)

    # Trending items logic START (Circular Queue potential)
    trendingQuery = None # Create function in app_db that'll take 50 random listed items
    trending = []
    # Trending items logic END

    return render_template('home.html', user=user)
 
@app.route("/inventory")
def inventory():
    steam_id = session.get("steam_id")
    if steam_id:
        user = get_user_info(steam_id)
    
<<<<<<< HEAD
    #inventory = fetch_cs_inventory('76561198045277210') #OHNE PIXEL INVENTORY
=======
    #inventory = fetch_cs_inventory('76561198045277210') #OHNE PIXEL INVENTORY ||| FOR TESTING |||
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
    inventory = fetch_cs_inventory(steam_id)
    if inventory:
        inventory = parse_inventory(inventory)
    
    return render_template('inventory.html', steam_id=steam_id, inventory=inventory, user=user)

@app.route("/inventory/list_item/", methods=['GET', 'POST'])
def list_item():
    # VALIDATION START
<<<<<<< HEAD
    """Nothing for now"""
=======
    """Make sure that the user has that item with the same assetid, classid and instanceid in his inventory"""
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
    # VALIDATION END

    steam_id = session.get("steam_id") # fetch steam id
    seller_id = get_user_info(steam_id).user_id # get user id (seller_id) on platform

<<<<<<< HEAD
    asset_id = int(request.form['asset_id'])
    market_name = request.form['market_name']
    price = float(request.form['price'])
    icon_url = request.form['icon_url']

    # LISTING
    new_listing_data = Listing(seller_id, market_name, asset_id, price, icon_url)
    listing_created = create_listing(new_listing_data)
    if listing_created:
        return redirect(url_for("inventory"))
    return "<h1>Item already listed</h1>"
=======
    assetid = int(request.form['assetid'])
    classid = int(request.form['classid'])
    instanceid = int(request.form['instanceid'])

    market_name = str(request.form['market_name'])
    icon_url = request.form['icon_url']
    inspect_link = request.form['inspect_link']
    
    if inspect_link == 'None':
        inspect_link = None

    price = float(request.form['price'])

    # LISTING
    assetData = get_asset_data_byname(market_name)
    if not assetData:
        return "Invalid item"
    
    asset_id = assetData.id
    
    listing_created = create_listing(seller_id, asset_id, assetid, classid, instanceid, price, icon_url, inspect_link)
    if listing_created:
        return redirect(url_for("inventory"))
    
    return "Item already listed"
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)

@app.route("/mylistings")
def mylistings():
    steam_id = session.get("steam_id", None)
    user = get_user_info(steam_id)
<<<<<<< HEAD
=======
    listings = None
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
    if user:
        listings = user_listings(user.user_id)
    return render_template("mylistings.html", user=user, listings=listings)

<<<<<<< HEAD
@app.route("/mylistings/delete", methods=['GET', 'POST'])
def mylistings_delete():
    seller_id = int(request.form['seller_id'])
    # Validate that user in session is one deleting the listing
    if session.get('user_id') == seller_id: 
        listing_id = int(request.form['listing_id'])
        delete_listing(listing_id)
        return redirect(url_for('mylistings'))
    return "Invalid"

=======
>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
@app.route("/mylistings/edit", methods=['GET', 'POST'])
def mylistings_edit():
    seller_id = int(request.form['seller_id'])
    # Validate that user in session is one editing the listing's price
    if session.get('user_id') == seller_id:
        listing_id = int(request.form['listing_id'])
        new_price = float(request.form['new_price'])
        edit_price(listing_id, new_price)
        return redirect(url_for('mylistings'))
    return "Invalid"

<<<<<<< HEAD
=======
@app.route("/mylistings/delete", methods=['GET', 'POST'])
def mylistings_delete():
    seller_id = int(request.form['seller_id'])
    # Validate that user in session is one deleting the listing
    if session.get('user_id') == seller_id: 
        listing_id = int(request.form['listing_id'])
        delete_listing(listing_id)
        return redirect(url_for('mylistings'))
    return "Invalid"

# MARKET START
@app.route("/market")
def market():
    steam_id = session.get("steam_id")
    user = None
    if steam_id:
        user = get_user_info(steam_id)
        print("Pass")
    
    assets = marketplace_data()
    return render_template('market.html', user=user, assets=assets)

@app.route("/market/item/<int:assetId>")
def market_item(assetId):
    steam_id = session.get("steam_id")
    user = None
    if steam_id:
        user = get_user_info(steam_id)

    asset_data = get_asset_data_byid(assetId)
    listings = get_listings(assetId)
    return render_template('market_item.html', asset=asset_data, listings=listings, user=user)

# MARKET END

>>>>>>> b7a7baa (feat: add public marketplace with live listings, item count, and price sorting)
# LOGIN START #
@app.route("/login")
def login():
    """Redirects users to Steam's OpenID login page"""
    return_to_url = f"{URL}/after_login"
    steam_login_url = (
        f"{STEAM_OPENID_URL}?"
        "openid.ns=http://specs.openid.net/auth/2.0&"
        "openid.mode=checkid_setup&"
        f"openid.return_to={return_to_url}&"
        f"openid.realm={URL}/&"  # Make sure this matches your Flask app's URL
        "openid.identity=http://specs.openid.net/auth/2.0/identifier_select&"
        "openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
    )
    print(f"Redirecting to: {steam_login_url}")  # Debugging
    return redirect(steam_login_url)

@app.route("/after_login")
def after_login():
    """Handles Steam OpenID response"""
    if "openid.identity" not in request.args:
        return "Steam login failed", 400

    # Extract Steam ID from OpenID URL
    steam_id = request.args["openid.identity"].split("/")[-1]

    # Verify OpenID response
    openid_params = {key: request.args[key] for key in request.args}
    openid_params["openid.mode"] = "check_authentication"

    response = requests.post(STEAM_OPENID_URL, data=openid_params)
    if "is_valid:true" not in response.text:
        return "Steam login validation failed", 400

    session["steam_id"] = steam_id  # Store in session
    
    # Checks if user is new or returning - If new, data is stored in DB
    if not user_exists(steam_id):
        user_data = fetch_steam_user_info(steam_id)
        store_new_user(user_data)
    
    # Adds the platform's unique user_id to the Secure-session cookie
    user = get_user_info(steam_id)
    session["user_id"] = user.user_id

    # Update last login.
    update_last_login(user.user_id)

    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("steam_id", None)
    session.pop("user_id", None)

    return redirect(url_for("home"))
# LOGIN END #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)