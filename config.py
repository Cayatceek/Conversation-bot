import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#MODEL_NAME = "gpt-4o-mini"
MODEL_NAME = "google/gemini-2.0-pro-exp-02-05:free"
# MODEL_NAME = "google/gemini-2.0-flash-lite-preview-02-05:free"