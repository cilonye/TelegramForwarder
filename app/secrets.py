from cryptography.fernet import Fernet
from dotenv import dotenv_values
from paths import ENV_FILE, SECRET_KEY_FILE

def get_secret(key):
    cipher = Fernet(SECRET_KEY_FILE.read_bytes())
    value = dotenv_values(ENV_FILE).get(key)
    return cipher.decrypt(value.encode()).decode()
