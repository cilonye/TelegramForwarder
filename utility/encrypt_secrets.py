import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# THE FIX: Add the project root to sys.path so 'app' is importable
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from cryptography.fernet import Fernet
from app.paths import SECRET_KEY_FILE, ENV_FILE

cipher = Fernet(SECRET_KEY_FILE.read_bytes())

api_id = input("API ID: ")
api_hash = input("API HASH: ")
phone = input("PHONE: ")

with open(ENV_FILE, "w") as f:
    f.write(f"API_ID={cipher.encrypt(api_id.encode()).decode()}\n")
    f.write(f"API_HASH={cipher.encrypt(api_hash.encode()).decode()}\n")
    f.write(f"PHONE={cipher.encrypt(phone.encode()).decode()}\n")
