from fastapi import HTTPException

from src.api.dependencies import UserIdDep
from src.exceptions import ObjectNotFoundException, AllRoomsAreBookedException
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.services.base import BaseService


class BookingService(BaseService):
    async def get_all_bookings(self):
        result = await self.db.bookings.get_all()
        return result

    async def get_all_my_bookings(self, user_id: UserIdDep):
        result = await self.db.bookings.get_filtered(user_id=user_id)
        if not result:
            raise HTTPException(status_code=404, detail="У вас нет бронированей)")
        return result

    async def check_booking_exists(self, data: BookingAddRequest):
        try:
            await self.db.rooms.get_one(id=data.room_id)
        except ObjectNotFoundException:
            raise HTTPException(status_code=400, detail="Номер не найден")

    async def add_booking(self, data: BookingAddRequest, user_id: UserIdDep):
        room = await self.db.rooms.get_one(id=data.room_id)
        hotel = await self.db.hotels.get_one(id=room.hotel_id)
        room_price: int = room.price

        _booking_data = BookingAdd(user_id=user_id, price=room_price, **data.model_dump())

        try:
            result = await self.db.bookings.add_booking(_booking_data, hotel)
        except AllRoomsAreBookedException as ex:
            raise HTTPException(status_code=409, detail=ex.detail)

        await self.db.commit()
        return result
