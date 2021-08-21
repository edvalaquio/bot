import os

from dotenv import load_dotenv

load_dotenv()

BOT_KEY = os.getenv("BOT_KEY")
GSPREAD_CREDENTIALS_LOCATION = os.getenv("GSPREAD_CREDENTIALS_LOCATION")
