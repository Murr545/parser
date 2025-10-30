import aiohttp
from src.parser.base_service import BaseParserService


class MercariParserService(BaseParserService):
    async def _fetch_items(self, url: str):
        api = "https://api.mercari.com/v1/items"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(
                    api,
                    proxy=self.proxies.get("http") if self.proxies else None,
                    timeout=20
                ) as resp:
                    data = await resp.json()
            except Exception as e:
                print(f"[HTTP ERROR] Mercari: {e}")
                return []

        items = []
        for item in data.get("data", []):
            items.append({
                "title": item.get("name", "Без названия"),
                "price": f"${item.get('price')}",
                "link": f"https://www.mercari.com/us/item/{item.get('id')}/",
                "image": item.get("thumbnails", [None])[0]
            })
        return items
