from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from src.logger.logger import get_logger
from src.bot.handlers.main import on_add_website, handle_website_url, handle_description
from src.bot.states.link_states import AddWebSite

logger = get_logger(__name__)
website_router = Router()

@website_router.callback_query(F.data == "add_website")
async def add_website_router(callback: CallbackQuery, state: FSMContext):
    await on_add_website(callback)
    await state.set_state(AddWebSite.waiting_for_url)


@website_router.message(AddWebSite.waiting_for_url)
async def add_website_link_router(message: Message, state: FSMContext):
    await handle_website_url(message)
    await state.set_state(AddWebSite.waiting_for_description)

@website_router.message(AddWebSite.waiting_for_description)
async def add_website_description_router(message: Message, state: FSMContext):
    await handle_description(message)
