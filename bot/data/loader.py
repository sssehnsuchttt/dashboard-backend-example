from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.data.config import token

bot = Bot(token=token, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler()