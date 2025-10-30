from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Конфигурация загрузки переменных
    model_config = ConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",  # ищет .env в корне проекта
        env_file_encoding="utf-8",
        extra="allow"
    )

    # --- Настройки Telegram ---
    BOT_TOKEN: str

    # --- Настройки БД
    DATABASE_URL: str

# --- Создаём экземпляр настроек ---
settings = Settings()