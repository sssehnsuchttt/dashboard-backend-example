from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from bot.services.api_sqlite import fetch_data
from bot.data.config import admin_id

class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        if message.from_user.id == admin_id:
            return True
        else:
            return False

class IsWork(BoundFilter):
    async def check(self, message: types.Message):
        settings = fetch_data("settings")

        if settings["is_working"] == 1 or message.from_user.id == admin_id:
            return False
        else:
            return True

class IsBanned(BoundFilter):
    async def check(self, message: types.Message):
        user_id = message.from_user.id
        if fetch_data("banlist", "fetchone", userid=user_id):
            return True
        else:
            return False