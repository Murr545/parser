from aiogram.fsm.state import State, StatesGroup

class AddWebSite(StatesGroup):
    waiting_for_url = State()
    waiting_for_description = State()
