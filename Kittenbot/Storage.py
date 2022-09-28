import os

from dotenv import load_dotenv
load_dotenv()

#Bot Token
#You need to setup a .env file with the bot key
BotKey = os.getenv("BOT_KEY")
TwitchKey = os.getenv("TWITCH_TOKEN")
TwitchClient = os.getenv("TWITCH_CLIENT")

#holds bot client
Client = ""