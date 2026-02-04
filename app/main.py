import asyncio
import signal
from forwarder import TelegramForwarder
from secrets import get_secret
from config_loader import load_config
from health import set_health
from paths import CONFIG_FILE

shutdown_event = asyncio.Event()

def _shutdown(*_):
    set_health("STOPPING")
    shutdown_event.set()

async def main():
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    set_health("STARTING")

    api_id = int(get_secret("API_ID"))
    api_hash = get_secret("API_HASH")
    phone = get_secret("PHONE")

    config = load_config(CONFIG_FILE)

    forwarder = TelegramForwarder(api_id, api_hash, phone, config)
    set_health("RUNNING")

    await forwarder.run(shutdown_event)
    set_health("STOPPED")

if __name__ == "__main__":
    asyncio.run(main())
