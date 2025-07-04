from dotenv import load_dotenv
import os

load_dotenv()
class Config():
    
    # === DB Related ===
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # === Steam Secrets ===
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")

    # === Flask Secrets ===
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # === Cryptography ===
    FERNET_KEY = os.getenv("FERNET_KEY")

    # === Web3 Secrets ===
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    INFURA_URL = os.getenv("INFURA_URL")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
    CHAIN_ID = os.getenv("CHAIN_ID")