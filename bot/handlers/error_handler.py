from bot.data.loader import dp


from aiogram.utils.exceptions import (Unauthorized)

@dp.errors_handler()
async def errors_handler(update, exception):
    if isinstance(exception, Unauthorized):
        return True