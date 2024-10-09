# - *- coding: utf- 8 - *-
from aiogram import Dispatcher

from .new_admin import AdminCheckMiddleware

# Подключение милдварей
def setup_middlewares(dp: Dispatcher):
    dp.middleware.setup(AdminCheckMiddleware())