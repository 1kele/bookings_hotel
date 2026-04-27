from fastapi import APIRouter, HTTPException

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("")
@cache(expire=30)
async def get_all_bookings(db: DBDep):
    result = await db.bookings.get_all()
    return {"status": "OK", "data": result}


@router.get("/me")
async def get_all_my_bookings(db: DBDep, user_id: UserIdDep):
    result = await db.bookings.get_filtered(user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="У вас нет бронированей)")
    return {"status": "OK", "data": result}


@router.post("")
async def add_booking(
    data: BookingAddRequest,
    db: DBDep,
    user_id: UserIdDep,
):
    room = await db.rooms.get_one_or_none(id=data.room_id)
    hotel = await db.hotels.get_one_or_none(id=room.hotel_id)
    room_price: int = room.price
    _booking_data = BookingAdd(user_id=user_id, price=room_price, **data.model_dump())
    result = await db.bookings.add_booking(_booking_data, hotel)
    await db.commit()
    return {"status": "OK", "data": result}
