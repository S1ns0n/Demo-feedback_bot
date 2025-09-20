import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = os.getenv("BOT_TOKEN")
SCENARIOS_DIR = ("D:/Coding/ProjPy/Demo-feedback bot/bot/scenarios")