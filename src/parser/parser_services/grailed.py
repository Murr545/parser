import aiohttp
from src.parser.base_service import BaseParserService


class GrailedParserService(BaseParserService):
    async def _fetch_items(self, url: str):
        api = "https://www.grailed.com/api/listings"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(
                    api,
                    proxy=self.proxies.get("http") if self.proxies else None,
                    timeout=20
                ) as resp:
                    data = await resp.json()
            except Exception as e:
                print(f"[HTTP ERROR] Grailed: {e}")
                return []

        items = []
        for item in data.get("data", []):
            items.append({
                "title": item.get("title", "Без названия"),
                "price": f"${item.get('price')} USD",
                "link": f"https://www.grailed.com/listings/{item.get('id')}",
                "image": item.get("photo_url")
            })
        return items