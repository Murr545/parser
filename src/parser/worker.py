import asyncio
import json
import os
import aio_pika
from dotenv import load_dotenv
from src.parser.parser_manager import ParserManager
from src.parser.utils.notifier import Notifier

load_dotenv()

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost/')
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'tasks')

async def main():
    notifier = Notifier()
    parser_manager = ParserManager(notifier)

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(RABBITMQ_QUEUE, durable=True)

    print('📡 Parser Service запущен и слушает очередь...')

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(requeue=False):
                try:
                    data = json.loads(message.body)
                    url = data['url']
                    user_id = data['user_id']
                    print(f"[TASK] Получена ссылка от пользователя {user_id}: {url}")
                    parser_manager.parse(url, user_id)
                except Exception as e:
                    print(f"[ERROR] Ошибка при обработке задачи: {e}")
                    # при ошибке можно явно nack и requeue
                    try:
                        await message.nack(requeue=True)
                    except Exception:
                        pass

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Завершение...')