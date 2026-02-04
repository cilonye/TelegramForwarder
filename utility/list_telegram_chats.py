import asyncio
import os
from telethon import TelegramClient, errors
from telethon.tl.types import User, Chat, Channel

CREDENTIALS_FILE = "credentials.txt"


# ----------------------------
# Credentials helpers
# ----------------------------
def read_credentials():
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            api_id = file.readline().strip()
            api_hash = file.readline().strip()
            phone_number = file.readline().strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        return None, None, None


def write_credentials(api_id, api_hash, phone_number):
    with open(CREDENTIALS_FILE, "w") as file:
        file.write(f"{api_id}\n{api_hash}\n{phone_number}\n")


def cleanup_credentials():
    try:
        if os.path.exists(CREDENTIALS_FILE):
            os.remove(CREDENTIALS_FILE)
            print(" credentials.txt has been securely removed.")
    except Exception as e:
        print(f" Failed to clean credentials.txt: {e}")


# ----------------------------
# Telegram Chat Lister
# ----------------------------
class TelegramChatLister:
    def __init__(self, api_id, api_hash, phone_number):
        self.phone_number = phone_number
        self.client = TelegramClient(
            session=f"session_{phone_number}",
            api_id=api_id,
            api_hash=api_hash
        )

    async def authorize(self):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(
                    self.phone_number,
                    input("Enter the login code: ")
                )
            except errors.SessionPasswordNeededError:
                password = input("Two-step verification enabled. Enter password: ")
                await self.client.sign_in(password=password)

    async def list_chats(self):
        await self.authorize()

        dialogs = await self.client.get_dialogs()
        output_file = f"chats_of_{self.phone_number}.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            for dialog in dialogs:
                entity = dialog.entity

                if isinstance(entity, User):
                    chat_type = "Private"
                    title = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                elif isinstance(entity, Chat):
                    chat_type = "Group"
                    title = entity.title
                elif isinstance(entity, Channel):
                    chat_type = "Channel" if entity.broadcast else "Supergroup"
                    title = entity.title
                else:
                    chat_type = "Unknown"
                    title = dialog.title

                line = f"{chat_type:12} | ID: {dialog.id} | {title}"
                print(line)
                f.write(line + "\n")

        print(f"\n Chats saved to: {output_file}")

        await self.client.disconnect()

        # CLEAN UP CREDENTIALS AFTER SUCCESS
        cleanup_credentials()


# ----------------------------
# Main
# ----------------------------
async def main():
    api_id, api_hash, phone_number = read_credentials()

    if not api_id:
        api_id = input("Enter API ID: ")
        api_hash = input("Enter API Hash: ")
        phone_number = input("Enter phone number (Include the country code): ")
        write_credentials(api_id, api_hash, phone_number)

    lister = TelegramChatLister(api_id, api_hash, phone_number)
    await lister.list_chats()


if __name__ == "__main__":
    asyncio.run(main())
