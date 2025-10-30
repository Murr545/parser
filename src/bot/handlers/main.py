from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from src.bot.services.send_to_rabbit import send_task_to_queue
from src.db.database import Website, User, get_session
from src.logger.logger import get_logger

logger = get_logger(__name__)

user_sites = {}
last_warning_messages = {}


async def on_add_website(callback: CallbackQuery):
    await callback.message.answer("Введите URL вашего сайта (начиная с http:// или https://):")
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Добавить сайт'")


async def handle_website_url(message: Message):
    user_sites[message.from_user.id] = {"url": message.text}
    await message.answer("Теперь введите описание вашего сайта:")
    logger.info(f"Пользователь {message.from_user.id} ввёл URL: {message.text}")


async def handle_description(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    description = message.text
    url = user_sites[user_id]["url"]

    session = await get_session()

    async with session as s:
        try:
            # 1️⃣ Ищем пользователя по int, а не str
            result = await s.execute(select(User).where(User.tg_id == int(user_id)))
            user = result.scalars().first()

            # 2️⃣ Если нет — создаём
            if not user:
                user = User(
                    tg_id=int(user_id),
                    username=username,
                    first_name=first_name
                )
                s.add(user)
                await s.commit()
                await s.refresh(user)

            # 3️⃣ Добавляем сайт
            new_site = Website(
                user_id=user.id,
                url=url,
                description=description
            )
            s.add(new_site)
            await s.commit()

            # 4️⃣ Отправляем задачу в RabbitMQ (user_id — tg_id из Telegram)
            send_task_to_queue(url, int(user_id))

            await message.answer("✅ Сайт добавлен и отправлен на проверку!")
            logger.info(f"Пользователь {user_id} успешно добавил сайт {url}")

        except Exception as e:
            await s.rollback()
            logger.error(f"[DB ERROR] {e}")
            await message.answer("❌ Ошибка при сохранении сайта в базу.")
