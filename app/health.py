from paths import HEALTH_FILE, RUNTIME_DIR

def set_health(state):
    RUNTIME_DIR.mkdir(exist_ok=True)
    with open(HEALTH_FILE, "w") as f:
        f.write(state)
