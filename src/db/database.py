import os
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP, JSON, BigInteger
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Берём строку подключения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,    # проверяет соединение перед использованием
    pool_recycle=1800,     # пересоздаёт соединение каждые 30 минут
)

# Фабрика асинхронных сессий
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
# Базовая модель
Base = declarative_base()


# ======================================================
#                   МОДЕЛИ ТАБЛИЦ
# ======================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)

    websites = relationship("Website", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id}, username={self.username})>"


class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    url = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_checked = Column(TIMESTAMP(timezone=True))
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="websites")
    parsing_results = relationship("ParsingResult", back_populates="website", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="website", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Website(id={self.id}, url={self.url})>"


class ParsingResult(Base):
    __tablename__ = "parsing_results"

    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"))
    content_hash = Column(String(64))
    parsed_data = Column(JSON)
    parsed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    website = relationship("Website", back_populates="parsing_results")

    def __repr__(self):
        return f"<ParsingResult(id={self.id}, website_id={self.website_id}, parsed_at={self.parsed_at})>"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"))
    message = Column(Text)
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
    website = relationship("Website", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, website_id={self.website_id})>"


# ======================================================
#             ФУНКЦИИ ДЛЯ РАБОТЫ С БД
# ======================================================

async def get_session() -> AsyncSession:
    """Создаёт и возвращает новую асинхронную сессию"""
    return async_session()
