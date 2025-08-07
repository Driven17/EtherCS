from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_migrate import Migrate

from app_fetch import fetch_steam_info, fetch_inventory
from app_config import Config
from app_encryption import encrypt, decrypt
from app_steam import parse_and_sort_inventory
from app_models import db
from app_db import (
    is_user, update_last_login, create_user, get_user_by_user_id, get_user_by_steam_id, 
    insert_listing, build_listings_by_seller, update_listing_price, delete_listing,
    get_asset_data_by_name, get_asset_data_by_id, get_listings_by_asset, build_marketplace_data,
    update_user_settings, get_listing_by_id, edit_listing_status, create_transaction, edit_transaction_status,
    get_sales_by_user_id, get_purchases_by_user_id, get_buyer_and_seller, build_trade_payload,
    insert_trade_offer_id, get_pending_trades_by_user, get_transaction_id_by_offer_id,
    get_listing_id_by_transaction_id, is_listing
)

from functools import wraps
import requests
import logging

# LOGGING INITIALIZATION
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# CONSTANTS
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
BASE_URL = "http://ethercs.com:3000"
DEVELOPER_IDS = {1, 2}

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
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def authorization_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify(success=False, reason="Not Authorized"), 401
        return f(*args, **kwargs)
    return wrapper

def developer_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('home'))
        if session.get('user_id') not in DEVELOPER_IDS:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    user = get_user_by_user_id(session.get('user_id'))
    return render_template('home.html', user=user)

### USER DASHBOARD SECTIONS START ###
@app.route("/inventory/")
@login_required
def inventory():
    user = get_user_by_user_id(session.get('user_id'))
    steam_id = session.get('steam_id')
    inventory = parse_and_sort_inventory(fetch_inventory(steam_id))
    return render_template('inventory.html', steam_id=steam_id, inventory=inventory, user=user)

@app.route("/inventory/list", methods=['POST'])
@login_required
def list_item():

    # VALIDATION REQUIRED HERE
    # VALIDATION REQUIRED HERE
    # VALIDATION REQUIRED HERE

    seller_id = session.get("user_id") # get user id (seller_id) on platform
    assetid = int(request.form['assetid'])

    if is_listing(assetid, seller_id):
        return "Item already listed"
    
    market_name = str(request.form['market_name'])
    icon_url = request.form['icon_url']
    inspect_link = request.form['inspect_link']
    
    if inspect_link == 'None':
        inspect_link = None
    
    price = float(request.form['price'])

    asset_data = get_asset_data_by_name(market_name)
    if not asset_data:
        return "Invalid item"
    
    listing_created = insert_listing(seller_id, asset_data.id, assetid, price, icon_url, inspect_link)
    if listing_created:
        return redirect(url_for("inventory"))
    
    return "Item already listed"

@app.route("/my-listings/")
@login_required
def my_listings():
    user = get_user_by_user_id(session.get('user_id'))
    listings = build_listings_by_seller(user.id)
    return render_template("my-listings.html", user=user, listings=listings)

@app.route("/my-listings/edit", methods=['POST'])
@login_required
def my_listings_edit():
    seller_id = int(request.form['seller_id'])

    # Validate that user in session is one editing the listing's price
    if session.get('user_id') == seller_id:

        listing_id = int(request.form['listing_id'])
        new_price = float(request.form['new_price'])

        update_listing_price(listing_id, new_price)
        return redirect(url_for('my_listings'))
    return "Invalid"

@app.route("/my-listings/delete", methods=['POST'])
@login_required
def my_listings_delete():
    seller_id = int(request.form['seller_id'])

    # Validate that user in session is one deleting the listing
    if session.get('user_id') == seller_id: 
        listing_id = int(request.form['listing_id'])
        delete_listing(listing_id)
        return redirect(url_for('my_listings'))
    return "Invalid"

@app.route("/my-sales")
@login_required
def my_sales():
    user = get_user_by_user_id(session.get('user_id'))
    sales = get_sales_by_user_id(user.id)  
    return render_template("my-sales.html", user=user, sales=sales)

@app.route("/my-purchases")
@login_required
def my_purchases():
    user = get_user_by_user_id(session.get('user_id'))
    purchases = get_purchases_by_user_id(user.id)
    return render_template("my-purchases.html", user=user, purchases=purchases)
### USER DASHBOARD SECTIONS END ###

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
    return render_template('market-item.html', asset=asset_data, listings=listings, user=user)
### MARKET END ###

### LOGIN START ###
@app.route("/login")
def login():
    """Redirects users to Steam's OpenID login page"""
    return_to_url = f"{BASE_URL}/{url_for("after_login")}"
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

@app.route("/after-login")
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
def logout():
    session.clear()
    return redirect(url_for("home"))
### LOGIN END ###

@app.route('/settings')
@login_required
def settings():
    user = get_user_by_user_id(session.get('user_id'))
    return render_template('settings.html', user=user)

### ALL AJAX ROUTES / API ROUTES ##
@app.route("/api/me/save-settings", methods=['POST'])
def save_user_settings():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()

    setting = data.get("setting")
    value = data.get("value")

    user_id = session.get("user_id")
    
    valid_settings = {"steam_api_key", "trade_link", "wallet_address", "trade_access_token"}
    if setting not in valid_settings:
        return jsonify({"message": "Invalid setting"}), 400

    if setting in {"steam_api_key", "trade_link", "trade_access_token"}:
        value = None if value == '' else encrypt(value)
    else:
        value = None if value == '' else value

    success = update_user_settings(user_id, setting, value)
    return jsonify({"message": "Success" if success else "Failed."}), 200 if success else 500

@app.route("/api/buy-listing", methods=['POST'])
@authorization_required
def buy_listing():

    buyer_id = session.get('user_id')

    data = request.get_json()
    listing_id = data.get('listing_id')

    # 1 confirm purchase went through and funds are in smart contract
    """Pass for now"""

    # 2 lock listing
    edit_listing_status(listing_id, 'Locked')

    # 3 fetch listing details
    listing = get_listing_by_id(listing_id)
    if not listing:
        return jsonify({'success': False, 'error': 'Listing not found'}), 404
    
    seller_id = listing.seller_id
    amount = listing.price

    asset_id = listing.asset_id
    market_name = get_asset_data_by_id(asset_id).name
    
    # 4 start a transaction record
    transaction_hash = "0x44"
    create_transaction(buyer_id, seller_id, listing_id, amount, transaction_hash)

    # 5 notify seller
    ###create_notification(
    ###    seller_id,
    ###    f"Your listing for '{market_name}' has been bought, "
    ###    "you have 12 hours to accept the sale."
    ###    )

    return jsonify({'success': True})

@app.route("/api/get-trade-payload/<int:transaction_id>", methods=['GET'])
@authorization_required
def get_trade_payload(transaction_id):

    if not transaction_id:
        return jsonify(success=False), 403
    
    # VALIDATION START
    user_id = session.get('user_id')
    seller_id = get_buyer_and_seller(transaction_id).get("seller_id") # Get seller UserID from transaction

    if not user_id == seller_id:
        return jsonify("Unauthorized"), 401
    # VALIDATION END

    payload = build_trade_payload(transaction_id)
    if not payload.get("buyer_trade_token"):
        return jsonify(success=False, message="Buyer trade link not found"), 403
    
    return jsonify(success=True, payload=payload), 200

@app.route("/api/accept-trade/<int:transaction_id>", methods=['POST'])
@authorization_required
def accept_trade(transaction_id):
    
    if not transaction_id:
        return jsonify(success=False), 403

    
    # VALIDATION START
    user_id = session.get('user_id')
    seller_id = get_buyer_and_seller(transaction_id).get("seller_id") # Get seller UserID from transaction

    if not user_id == seller_id:
        return jsonify("Unauthorized"), 401
    # VALIDATION END

    edit_transaction_status(transaction_id, 'AwaitingSellerAction')
    return jsonify(success=True), 200

@app.route("/api/send-trade-response", methods=['POST'])
@authorization_required
def send_trade_response():
    data = request.get_json()

    transaction_id = data.get("transaction_id")
    trade_offer_id = data.get("trade_offer_id")

    if not transaction_id or not trade_offer_id:
        return jsonify({"success": False, "error": "Missing data"}), 400

    # Verify seller is owner of this transaction
    user_id = int(session.get('user_id'))
    transaction_info = get_buyer_and_seller(transaction_id)
    seller_id = int(transaction_info.get("seller_id"))

    if not user_id == seller_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # Insert trade offer id into database to track trade
    insert_trade_offer_id(transaction_id, trade_offer_id)
    # Save the trade offer ID and mark transaction as 'TradeSent'
    success = edit_transaction_status(transaction_id, 'TradeSent')

    # Notify buyer to accept trade
    buyer_id = transaction_info.get("buyer_id")
    seller = get_user_by_user_id(user_id)
    ###create_notification(
    ###    buyer_id,
    ###    f"Seller, {seller.name}, has just sent you a trade. ",
    ###    "You have 12 hours to accept it."
    ###)

    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "error": "DB update failed"}), 500

@app.route("/api/me/get-pending-trades", methods=['GET'], strict_slashes=False)
@authorization_required
def get_pending_trades():
    user_id = session.get("user_id")
    trades = get_pending_trades_by_user(user_id)
    return jsonify(success=True, trades=trades)

@app.route("/api/me/process-matching-offers", methods=['POST'], strict_slashes=False)
@authorization_required
def process_matching_offers():
    offers = request.get_json()

    if not isinstance(offers, list):
        return jsonify(success=False, error="Expected a list of offers"), 400

    valid_states = [2, 3, 9, 11]

    for offer in offers:
        offer_state = offer.get("state")
        offer_id = offer.get("offer_id")

        if not offer_id or offer_state is None:
            logging.warning("Skipping invalid offer: %s", offer)
            continue

        if offer_state in [2, 9, 11]:
            continue

        if offer_state not in valid_states:
            status = "Failed"
        elif offer_state in [3, 11]:
            status = "Success"
        else:
            continue

        transaction_id = get_transaction_id_by_offer_id(offer_id)
        if not transaction_id:
            logging.error("No transaction found for offer_id %s", offer_id)
            continue

        listing_id = get_listing_id_by_transaction_id(transaction_id)
        if not listing_id:
            logging.error("No listing found for transaction_id %s", transaction_id)
            continue

        if status == "Failed":

            logging.info("Marking transaction #%s as Failed", transaction_id)

            edit_listing_status(listing_id, "Active")
            edit_transaction_status(transaction_id, "Failed")

        elif status == "Success":
            
            logging.info("Marking transaction #%s as Failed", transaction_id)

            edit_listing_status(listing_id, "Sold")
            edit_transaction_status(transaction_id, "Success")

    return jsonify(success=True), 200

### DEVELOPERS ###
@app.route("/debug")
@developer_only
def debug():
    return dict(session)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
