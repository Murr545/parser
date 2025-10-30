import asyncio
from aiogram import Bot, Dispatcher
from src.bot.routers import setup_routers
from src.core.config import settings
from src.logger.logger import setup_logging, get_logger

setup_logging(level=settings.log_level)
logger = get_logger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

setup_routers(dp)

async def main():
    logger.info("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())