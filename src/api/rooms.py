from datetime import date

from fastapi import APIRouter, Body, Query

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.exceptions import (
    HotelNotFoundHTTPException,
    RoomNotFoundHTTPException, RoomNotFoundException, HotelNotFoundException,
)
from src.schemas.rooms import RoomAddRequest, RoomPatchRequesst
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotel", tags=["Номера отелей"])


@router.get("/{hotel_id}/rooms")
@cache(expire=30)
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    data_from: date = Query(examples=["2026-04-17"]),
    data_to: date = Query(examples=["2026-04-25"]),
):
    result = await RoomService(db).get_rooms_filter_by_time(hotel_id, data_from, data_to)
    return {"data": result}


@router.get("/{hotel_id}/rooms/{room_id}")
@cache(expire=30)
async def get_one_room(
    room_id: int,
    hotel_id: int,
    db: DBDep,
):
    try:
        result = await RoomService(db).get_one_room(room_id,hotel_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return {"result": result}


@router.post("/{hotel_id}/rooms")
async def add_room(hotel_id: int, db: DBDep, data: RoomAddRequest = Body()):
    try:
        result = await RoomService(db).create_room(hotel_id, data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK", "data": result}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(hotel_id: int, db: DBDep, room_id: int, data: RoomAddRequest):
    try:
        await RoomService(db).update_room(hotel_id, room_id, data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_update_room(hotel_id: int, db: DBDep, room_id: int, data: RoomPatchRequesst):
    try:
        await RoomService(db).partially_update_room(hotel_id, room_id, data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    return {"status": "Ok"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        await RoomService(db).delete_room(hotel_id, room_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    return {"status": "Ok"}
