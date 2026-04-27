from fastapi import HTTPException
from sqlalchemy import select

from src.models import RoomsOrm
from src.schemas.bookings import BookingAdd, BookingAddRequest


class BookingService:

    def __init__(self, db):
        self.db = db