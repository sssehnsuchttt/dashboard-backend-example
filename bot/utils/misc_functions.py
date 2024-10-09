from aiogram import Dispatcher
from bot.services.api_session import AsyncSession
from bot.data.config import admin_id, token, web_url, bot_url, bot_url, bot_name
from bot.data.loader import bot
from bot.utils.text_strings import text
from bot.keyboards.keyboards import menu_keyboard

async def on_startup_notify(dp: Dispatcher, aSession: AsyncSession):
    try:
        website = f"{web_url}/panel?bot={bot_name}"
        msg_template = text("start_message_admin", admin_id)
        msg = msg_template.replace('{website}', website)
        await bot.send_message(admin_id, msg, reply_markup=menu_keyboard(admin_id))
    except Exception as e:
        print("Ошибка при запуске сервера:", e)          

async def set_bot_url(aSession: AsyncSession):
    session = await aSession.get_session()
    response = await session.get(f"https://api.telegram.org/bot{token}/setWebhook?url={web_url}/{bot_name}")
