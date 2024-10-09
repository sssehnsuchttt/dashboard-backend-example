from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from bot.utils.misc.bot_filters import IsAdmin
from bot.utils.text_strings import get_text, text
from bot.data.loader import dp
from bot.keyboards.inline_admin import open_webapp
from bot.services.api_sqlite import delete_data, update_data
import string
import random
import bcrypt

@dp.message_handler(IsAdmin(), text=get_text("personal_area"))
async def personal_area(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(f"<b>{text('personal_area', message.from_user.id)}:</b>", reply_markup=open_webapp(message))

@dp.message_handler(IsAdmin(), text=get_text("change_password"))
async def send_new_password(message: Message, state: FSMContext):
    await state.finish()

    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(8))

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    delete_data("tokens", db_path="web_admins.db")
    update_data("accounts", update={"password": hashed_password}, search={"username": "admin"}, db_path="web_admins.db")

    login = "admin"

    msg_template = text("new_password_message", message.from_user.id)

    msg = msg_template.replace('{login}', login).replace('{password}', password)

    await message.answer(msg)
