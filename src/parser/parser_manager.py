import asyncio
from typing import Dict

from sqlalchemy import func
from sqlalchemy.future import select

from src.parser.base_service import BaseParserService
from src.parser.utils.notifier import Notifier
from src.db.database import get_session, Website, ParsingResult, Notification, User

# Импорт конкретных парсеров
from src.parser.parser_services.vinted import VintedParserService
from src.parser.parser_services.grailed import GrailedParserService
from src.parser.parser_services.therealreal import TheRealRealParserService
from src.parser.parser_services.depop import DepopParserService
from src.parser.parser_services.mercari import MercariParserService
from src.parser.parser_services.poshmark import PoshmarkParserService

PARSER_MAP = {
    'vinted': VintedParserService,
    'grailed': GrailedParserService,
    'poshmark': PoshmarkParserService,
    'mercari': MercariParserService,
    'depop': DepopParserService,
    'therealreal': TheRealRealParserService
}

class ParserManager:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier
        self.parsers: Dict[str, BaseParserService] = {}
        self.tasks: Dict[str, asyncio.Task] = {}

    def _get_parser_for_url(self, url: str):
        for key, cls in PARSER_MAP.items():
            if key in url:
                return cls
        return None

    def parse(self, url: str, user_id: int):
        if url in self.tasks and not self.tasks[url].done():
            print(f"[INFO] Парсер для {url} уже запущен")
            return

        parser_cls = self._get_parser_for_url(url)
        if not parser_cls:
            print(f"[WARN] Не найден парсер для {url}")
            return

        parser = parser_cls(notify_callback=self._notify_user_and_save)
        self.parsers[url] = parser
        task = asyncio.create_task(parser.parse(url, user_id))
        self.tasks[url] = task
        print(f"[START] Запущен парсер для {url}")

    async def _notify_user_and_save(self, user_id: int, message: str, image_url: str | None = None):
        # --- Сначала сохраняем в БД ---
        try:
            await self._save_to_db(user_id, message)
        except Exception as e:
            print(f"[DB ERROR] Ошибка при сохранении: {e}")

        # --- Затем отправляем уведомление пользователю ---
        try:
            await self.notifier.send(user_id, message, image_url)
            if image_url:
                print(f"[NOTIFY] Отправлено сообщение с фото пользователю {user_id}")
            else:
                print(f"[NOTIFY] Отправлено сообщение без фото пользователю {user_id}")
        except Exception as e:
            print(f"[NOTIFY ERROR] {e}")

    async def _save_to_db(self, user_id: int, message: str):
        session = await get_session()
        async with session as s:
            try:
                result = await s.execute(select(User).where(User.tg_id == user_id))
                user = result.scalars().first()
                if not user:
                    print(f"[DB] Не найден пользователь с tg_id={user_id}")
                    return

                # Берём лишь сайты, привязанные к этому пользователю
                result = await s.execute(select(Website).where(Website.user_id == user.id))
                websites = result.scalars().all()

                for site in websites:
                    site.last_checked = func.now()
                    new_result = ParsingResult(website_id=site.id, parsed_data={"message": message}, content_hash="dummy_hash")
                    s.add(new_result)

                    notif = Notification(user_id=user.id, website_id=site.id, message=message)
                    s.add(notif)

                await s.commit()
                print(f"[DB] ✅ Сохранено уведомление для пользователя {user_id}")
            except Exception as e:
                await s.rollback()
                raise