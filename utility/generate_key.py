import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# THE FIX: Add the project root to sys.path so 'app' is importable
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cryptography.fernet import Fernet
from app.paths import SECRET_KEY_FILE

SECRET_KEY_FILE.write_bytes(Fernet.generate_key())
print("secret.key created")
