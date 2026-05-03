import asyncio
import logging
from time import sleep
from PIL import Image
import os

from src.database import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager


@celery_instance.task
def test_task():
    sleep(15)
    print("Я крутой все сделал")


@celery_instance.task
def resize_image(image_path: str):
    logging.debug(f"Вызывается функция с image_path: {image_path}")
    sizes = [size for size in range(10_000, 1_000_000, 1_000)]
    output_dir = "src/static/images"
    os.makedirs(output_dir, exist_ok=True)

    with Image.open(image_path) as img:
        filename = os.path.splitext(os.path.basename(image_path))[0]
        ext = os.path.splitext(image_path)[1]
        output_path = None
        for size in sizes:
            resized = img.copy()
            resized.thumbnail((size, size))
            output_path = os.path.join(output_dir, f"{filename}_{size}{ext}")
            resized.save(output_path)

    logging.info(f"Сохранено: {output_path}")


async def get_bookings_with_today_checkin_helper():
    logging.debug("Я начал работать")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        res = await db.bookings.get_bookings_with_today_checkin()
        logging.debug(f"{res}")


@celery_instance.task(name="booking_today_checkin")
def send_email_to_users_with_today_checkin():
    asyncio.run(get_bookings_with_today_checkin_helper())
