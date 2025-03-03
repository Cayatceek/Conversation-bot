import asyncio
import logging
import sys


from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN
from handlers.chat import chat_router  # AI-powered chat handler
from database.db import create_tables, save_user

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Include handlers (AI chat last)
dp.include_router(chat_router)  # AI chat should be last to prevent it from catching commands

@dp.message(Command("start"))
async def start_handler(message: Message):
    save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    await message.answer("Привет! Я Джарвис, твой лучший собеседник.")

async def main():
    """Main bot execution."""
    create_tables()  # Ensure the database is ready

    logging.info("Starting AI-powered bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        await bot.session.close()
        logging.info("Bot session closed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s - %(levelname)s - %(message)s")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped manually.")
