import aiohttp
from bs4 import BeautifulSoup
from src.parser.base_service import BaseParserService


class PoshmarkParserService(BaseParserService):
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
                print(f"[HTTP ERROR] Poshmark: {e}")
                return []

        soup = BeautifulSoup(html, "html.parser")

        items = []
        for item in soup.select("div.tile"):
            title_tag = item.select_one(".tile__title")
            price_tag = item.select_one(".p--t--1")
            link_tag = item.select_one("a")
            img_tag = item.select_one("img")

            if not link_tag:
                continue

            items.append({
                "title": title_tag.text.strip() if title_tag else "Без названия",
                "price": price_tag.text.strip() if price_tag else "—",
                "link": "https://poshmark.com" + link_tag["href"],
                "image": img_tag["src"] if img_tag else None
            })
        return items
