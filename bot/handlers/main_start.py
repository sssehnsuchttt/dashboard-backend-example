from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from bot.utils.text_strings import text
from bot.data.loader import dp
from bot.data.config import web_url, bot_url, admin_id, bot_name
from bot.keyboards.keyboards import menu_keyboard


start = ["/start"]
@dp.message_handler(text_startswith=start, state="*")
async def main_start(message: Message, state: FSMContext):
    await state.finish()
    msg = ""
    if str(message.from_user.id) == str(admin_id):
        website = f"{web_url}/panel?bot={bot_name}"
        msg_template = text("start_message_admin", message.from_user.id)
        msg = msg_template.replace('{website}', website)
    else:
        msg = text("start_message", message.from_user.id)   

    await message.answer(msg, reply_markup=menu_keyboard(message.from_user.id))