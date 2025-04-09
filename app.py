from flask import Flask, redirect, url_for, session, request
from flask_migrate import Migrate
from app_fetch import fetch_steam_user_info
from app_config import Config
from app_db import db, user_exists, store_new_user
import requests

# Init steam openID url without parameters
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
URL = "http://localhost:3000"

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app) # Initialize DB
migrate = Migrate(app, db) # Initialize Flask-Migrate
with app.app_context():
    db.create_all()

# Initial Home Page - Checks if Steam ID is already in session or not. If not there's a login to steam button
@app.route("/")
def home():
    steam_id = session.get("steam_id")
    if steam_id:    
        return f"Welcome! Your Steam ID is {steam_id} <br> <a href='/logout'>Logout</a>"
    return '<a href="/login">Login with Steam</a>'

# Initial login page
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

    return redirect(url_for("home"))

# Initial logout page
@app.route("/logout")
def logout():
    session.pop("steam_id", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)