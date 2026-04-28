import sqlalchemy
from datetime import date
from fastapi import APIRouter, HTTPException, Body, Query

from fastapi_cache.decorator import cache
from sqlalchemy.exc import NoResultFound

from src.api.dependencies import DBDep
from src.exceptions import ObjectNotFoundException, check_date_to_after_date_from, HotelNotFoundHTTPException, \
    RoomNotFoundHTTPException
from src.schemas.facilities import RoomsFacilityAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequesst, RoomPatch

router = APIRouter(prefix="/hotel", tags=["Номера отелей"])


@router.get("/{hotel_id}/rooms")
@cache(expire=30)
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    data_from: date = Query(examples=["2026-04-17"]),
    data_to: date = Query(examples=["2026-04-25"]),
):
    check_date_to_after_date_from(data_from, data_to)

    result = await db.rooms.get_rooms_filter_by(
        hotel_id=hotel_id, data_from=data_from, data_to=data_to
    )
    return {"data": result}


@router.get("/{hotel_id}/rooms/{room_id}")
@cache(expire=30)
async def get_one_room(
    room_id: int,
    db: DBDep,
):
    result = await db.rooms.get_one_or_none_with_rels(id=room_id)
    if not result:
        raise HTTPException(status_code=404,detail="Номер не найден")

    return {"result": result}


@router.post("/{hotel_id}/rooms")
async def add_room(hotel_id: int, db: DBDep, data: RoomAddRequest = Body()):

    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException

    _room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump())
    room = await db.rooms.add(_room_data)

    rooms_facilities_data = [
        RoomsFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in data.facilities_ids
    ]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()
    return {"status": "Ok", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(hotel_id: int, db: DBDep, room_id: int, data: RoomAddRequest):

    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException


    new_data = RoomAdd(hotel_id=hotel_id, **data.model_dump(exclude={"facilities_ids"}))
    await db.rooms_facilities.set_room_facilities(room_id, data.facilities_ids)
    await db.commit()
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_update_room(hotel_id: int, db: DBDep, room_id: int, data: RoomPatchRequesst):
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException


    _room_data_check = data.model_dump(exclude_none=True)
    _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_check)
    await db.rooms.edit(_room_data, exclude_unset=True, hotel_id=hotel_id, id=room_id)

    if "facilities_ids" in _room_data_check:
        await db.rooms_facilities.set_room_facilities(room_id, data.facilities_ids)
    await db.commit()
    return {"status": "Ok"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):

    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException

    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
    return {"status": "Ok"}
