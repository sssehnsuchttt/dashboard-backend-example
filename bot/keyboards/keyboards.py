from aiogram.types import ReplyKeyboardMarkup
from bot.utils.text_strings import text
from bot.data.config import admin_id

# Кнопки главного меню
def menu_keyboard(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if user_id == admin_id:
        keyboard.row(text("personal_area"))
        keyboard.row(text("change_password"))
    else:
        keyboard.row("Кнопка-заглушка")

    return keyboard