import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect("postgresql://postgres:admin@127.0.0.1:5432/postgres")
        print("✅ Успешно подключились к базе postgres!")

        # Проверим, есть ли база parser_db
        rows = await conn.fetch("SELECT datname FROM pg_database WHERE datname = 'parser_db'")
        if rows:
            print("📦 База данных parser_db уже существует.")
        else:
            await conn.execute("CREATE DATABASE parser_db;")
            print("✅ Создана база данных parser_db!")

        await conn.close()
    except Exception as e:
        print("❌ Ошибка подключения:", e)

asyncio.run(test())