from telethon import TelegramClient, events
from logger import get_logger

log = get_logger()

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone, config):
        self.client = TelegramClient(f"session_{phone}", api_id, api_hash)
        self.config = config

    async def run(self, shutdown_event):
        await self.client.start()

        @self.client.on(events.NewMessage(chats=self.config["telegram"]["source_chat_id"]))
        async def handler(event):
            if not event.text:
                return

            text = event.text.lower()
            keywords = self.config["telegram"].get("keywords", [])

            if keywords and not any(k in text for k in keywords):
                return

            for dest in self.config["telegram"]["destination_chat_ids"]:
                await self.client.send_message(dest, event.text)

        await shutdown_event.wait()
        await self.client.disconnect()
