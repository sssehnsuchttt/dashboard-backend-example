from aiogram.types import InlineKeyboardMarkup, WebAppInfo, KeyboardButton
from bot.data.config import web_url, bot_name
from bot.utils.text_strings import text


def open_webapp(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(KeyboardButton(text("personal_area", message.from_user.id), web_app=WebAppInfo(url=f"{web_url}/webapp?bot={bot_name}")))
    return keyboard