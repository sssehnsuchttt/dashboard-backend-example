from bot.services.api_sqlite import create_db
from bot.data.loader import scheduler
from bot.handlers import dp
from bot.data.loader import bot
from bot.data.config import port, bot_url
from bot.services.api_session import AsyncSession
from bot.utils.misc_functions import on_startup_notify, set_bot_url
from bot.middlewares import setup_middlewares
from aiohttp import web
import sys, os
import asyncio
from bot.web_app.loader import app
from aiogram.dispatcher.webhook import configure_app


aSession = AsyncSession()

configure_app(dp, app, f"/{bot_url}")

async def on_startup(app):
    dp.bot['aSession'] = aSession
    await on_startup_notify(dp, aSession)
    await set_bot_url(aSession)
    print("BOT WAS STARTED")

async def on_shutdown(app):
    aSession: AsyncSession = dp.bot['aSession']
    await aSession.close()

    await dp.storage.close()
    await dp.storage.wait_closed()
    await (await dp.bot.get_session()).close()

    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")

    print("Goodbye!")

if __name__ == "__main__":
    create_db()
    setup_middlewares(dp)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=port, handle_signals=True)
    #executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
