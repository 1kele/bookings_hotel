from fastapi import APIRouter

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("")
@cache(expire=30)
async def get_all_bookings(db: DBDep):
    result = await BookingService(db).get_all_bookings()
    return {"status": "OK", "data": result}


@router.get("/me")
async def get_all_my_bookings(db: DBDep, user_id: UserIdDep):
    result = await BookingService(db).get_all_my_bookings(user_id)
    return {"status": "OK", "data": result}


@router.post("")
async def add_booking(
    data: BookingAddRequest,
    db: DBDep,
    user_id: UserIdDep,
):
    await BookingService(db).check_booking_exists(data)
    result = await BookingService(db).add_booking(data, user_id)
    return {"status": "OK", "data": result}
