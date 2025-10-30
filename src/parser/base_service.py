import asyncio
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class BaseParserService:
    SCAN_INTERVAL = 60

    def __init__(self, notify_callback=None):
        self._known_items = {}
        self.notify_callback = notify_callback
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.proxies = self._load_proxies()

    def _load_proxies(self):
        user = os.getenv("PROXY_USER")
        password = os.getenv("PROXY_PASS")
        host = os.getenv("PROXY_HOST")
        port = os.getenv("PROXY_PORT")

        if not host or not port:
            return None

        auth = f"{quote_plus(user)}:{quote_plus(password)}@" if user and password else ""
        proxy_url = f"http://{auth}{host}:{port}"
        return {"http": proxy_url, "https": proxy_url}

    async def parse(self, url: str, user_id: int = None):
        # Запускаем цикл парсинга как задача
        if url not in self._known_items:
            self._known_items[url] = set()

        while True:
            try:
                items = await self._fetch_items(url)
                if not items:
                    await asyncio.sleep(self.SCAN_INTERVAL)
                    continue

                current_links = {i['link'] for i in items}
                known_links = self._known_items.get(url, set())

                new_links = current_links - known_links
                if new_links:
                    new_items = [i for i in items if i['link'] in new_links]
                    await self._on_new_items(url, new_items, user_id)
                    self._known_items[url].update(new_links)

            except Exception as e:
                print(f"[ERROR] Ошибка при парсинге {url}: {e}")

            await asyncio.sleep(self.SCAN_INTERVAL)

    async def _fetch_items(self, url: str):
        raise NotImplementedError("Реализуй в подклассе")

    async def _on_new_items(self, url: str, new_items: list, user_id: int = None):
        if not new_items:
            return

        for item in new_items:
            msg = (
                f"<b>{item['title']}</b>\n"
                f"{item.get('price', '—')}\n"
                f"<a href='{item['link']}'>Открыть объявление</a>"
            )
            print(f"[NEW ITEM] {msg}")

            image_url = item.get("image")

            if self.notify_callback and user_id:
                try:
                    if asyncio.iscoroutinefunction(self.notify_callback):
                        await self.notify_callback(user_id, msg, image_url)
                    else:
                        # синхронный callback — вызываем в threadpool
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(None, self.notify_callback, user_id, msg, image_url)
                except Exception as e:
                    print(f"[ERROR] Ошибка при уведомлении пользователя {user_id}: {e}")