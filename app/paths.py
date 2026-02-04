import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# THE FIX: Add the project root to sys.path so 'app' is importable
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

APP_DIR = PROJECT_ROOT / "app"
UTILITY_DIR = PROJECT_ROOT / "utility"
CONFIG_DIR = PROJECT_ROOT / "config"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
LOG_DIR = RUNTIME_DIR / "logs"

ENV_FILE = PROJECT_ROOT / ".env"
SECRET_KEY_FILE = PROJECT_ROOT / "secret.key"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
HEALTH_FILE = RUNTIME_DIR / "health.status"
LOG_FILE = LOG_DIR / "forwarder.log"
