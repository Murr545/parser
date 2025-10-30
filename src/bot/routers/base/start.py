from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.keyboards.site_keyboard import get_add_website_keyboard
from src.logger.logger import get_logger

logger = get_logger(__name__)
start_router = Router()

@start_router.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал /start")
    await message.answer(
        "👋 Привет! Я готов к работе. Введи /help, чтобы узнать команды.",
        reply_markup=get_add_website_keyboard()
    )

@start_router.message(Command("help"))
async def cmd_help(message: Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал /help")
    await message.answer("📋 Доступные команды:\n/start — начало работы\n/help — справка")