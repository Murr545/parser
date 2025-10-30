from aiogram import Dispatcher

from src.bot.routers.base.start import start_router
from src.bot.routers.base.website import website_router


def setup_routers(dp: Dispatcher):
    dp.include_router(website_router)
    dp.include_router(start_router)
