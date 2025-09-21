import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = os.getenv("BOT_TOKEN")
SCENARIOS_DIR = (f"{ROOT_DIR}/scenarios")
IMAGE_DIR = (f"{ROOT_DIR}/images")