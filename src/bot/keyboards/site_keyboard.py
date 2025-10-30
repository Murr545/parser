from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_add_website_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ Добавить ссылку на сайт",
                callback_data="add_website"
            )
        ],
        [
            InlineKeyboardButton(
                text="📜 Список ссылок",
                callback_data="list_websites"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Удалить ссылку",
                callback_data="delete_link"
            )
        ],
        [
            InlineKeyboardButton(
                text="❓ Помощь",
                callback_data="help"
            )
        ]
    ])