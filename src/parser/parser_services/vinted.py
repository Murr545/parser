import aiohttp
from bs4 import BeautifulSoup
from src.parser.base_service import BaseParserService


class VintedParserService(BaseParserService):
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
                print(f"[HTTP ERROR] Vinted: {e}")
                return []

        soup = BeautifulSoup(html, "html.parser")
        items = []

        for item in soup.select("div.feed-grid__item"):
            # --- Тайтл ---
            title_tag = item.select_one("[data-testid$='--description-title']")
            title = title_tag.text.strip() if title_tag else "Без названия"

            # --- Цена ---
            price_tag = item.select_one("[data-testid$='--price-text']")
            price = price_tag.text.strip() if price_tag else "—"

            # --- Ссылка ---
            link_tag = item.select_one("a.new-item-box__overlay")
            if not link_tag:
                continue

            link = link_tag.get("href", "")
            if not link.startswith("http"):
                link = "https://www.vinted.it" + link

            # --- Картинка ---
            img_tag = item.select_one("img.web_ui__Image__content") \
                or item.select_one("img[data-testid$='--image--img']")
            img_url = None
            if img_tag:
                img_url = img_tag.get("src")
                if img_url and img_url.startswith("/"):
                    img_url = "https://images1.vinted.net" + img_url
            print(img_url)
            # --- Добавляем товар ---
            items.append({
                "title": title,
                "price": price,
                "link": link,
                "image": img_url
            })

        print(f"[PARSED] Найдено {len(items)} товаров на Vinted")
        return items


# --- пример использования внутри твоего воркера ---
# async def process_vinted(url, user_id, bot):
#     parser = VintedParserService()
#     items = await parser._fetch_items(url)
#     for item in items:
#         msg = (
#             f"<b>{item['title']}</b>\n"
#             f"{item['price']}\n"
#             f"<a href='{item['link']}'>Открыть объявление</a>"
#         )
#         if item["image"]:
#             await bot.send_photo(chat_id=user_id, photo=item["image"], caption=msg, parse_mode="HTML")
#         else:
#             await bot.send_message(chat_id=user_id, text=msg, parse_mode="HTML")
