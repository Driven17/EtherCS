from cryptography.fernet import Fernet
from app_config import Config

key = Config.FERNET_KEY
if not key:
    raise ValueError("FERNET_KEY is not set in the environment.")

fernet = Fernet(key.encode())

# Encrypts a string value into bytes #
def encrypt(plaintext):
    return fernet.encrypt(plaintext.encode())

# Decrypts bytes into a string value #
def decrypt(ciphertext):
    return fernet.decrypt(ciphertext).decode()
