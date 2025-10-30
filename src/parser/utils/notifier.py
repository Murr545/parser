from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from src.core.config import settings


class Notifier:
    def __init__(self, token: str = None):
        token = token or settings.BOT_TOKEN
        self.bot = Bot(token=token)

    async def send(self, user_id: int, message: str, image_url: str | None = None):
        try:
            if image_url:
                # отправляем сообщение с картинкой
                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=image_url,
                    caption=message,
                    parse_mode="HTML"
                )
            else:
                # обычный текст без картинки
                await self.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="HTML",
                    disable_web_page_preview=False
                )

        except TelegramAPIError as e:
            print(f"[TELEGRAM ERROR] Не удалось отправить сообщение пользователю {user_id}: {e}")
        except Exception as e:
            print(f"[TELEGRAM ERROR] Unexpected error for user {user_id}: {e}")

    async def close(self):
        try:
            await self.bot.session.close()
        except Exception:
            pass
