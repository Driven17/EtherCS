from dotenv import load_dotenv
import os

load_dotenv()
class Config():
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")