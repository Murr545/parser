import aiohttp
from src.parser.base_service import BaseParserService


class DepopParserService(BaseParserService):
    async def _fetch_items(self, url: str):
        api = "https://webapi.depop.com/api/v2/search/"
        params = {"what": "shoes"}  # пример запроса
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(
                    api,
                    params=params,
                    proxy=self.proxies.get("http") if self.proxies else None,
                    timeout=20
                ) as resp:
                    data = await resp.json()
            except Exception as e:
                print(f"[HTTP ERROR] Depop: {e}")
                return []

        items = []
        for item in data.get("products", []):
            print(item)
            items.append({
                "title": item.get("slug", "Без названия"),
                "price": f"{item.get('price', {}).get('price_amount')} {item.get('price', {}).get('currency_name')}",
                "link": f"https://www.depop.com/products/{item.get('slug')}",
                "image": item.get("preview", {}).get("150")
            })
        return items