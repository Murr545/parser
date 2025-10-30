import aiohttp
from bs4 import BeautifulSoup
from src.parser.base_service import BaseParserService


class TheRealRealParserService(BaseParserService):
    async def _fetch_items(self, url: str):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(
                    url,
                    proxy=self.proxies.get("http") if self.proxies else None,
                    timeout=20
                ) as resp:
                    html = await resp.text()
            except Exception as e:
                print(f"[HTTP ERROR] TheRealReal: {e}")
                return []

        soup = BeautifulSoup(html, "html.parser")
        items = []

        # пример структуры карточек на TheRealReal:
        for card in soup.select("div.product-card"):
            title_tag = card.select_one("div.product-card__brand")
            price_tag = card.select_one("div.product-card__price")
            link_tag = card.select_one("a.product-card__link")
            img_tag = card.select_one("img.product-card__image")

            if not link_tag:
                continue

            link = "https://www.therealreal.com" + link_tag["href"]
            image = img_tag.get("src") if img_tag else None

            items.append({
                "title": title_tag.text.strip() if title_tag else "Без названия",
                "price": price_tag.text.strip() if price_tag else "—",
                "link": link,
                "image": image
            })

        print(f"[PARSED] Найдено {len(items)} товаров на TheRealReal")
        return items