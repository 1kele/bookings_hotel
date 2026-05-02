from datetime import date

from fastapi import Query, APIRouter, Body

from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import (
    ObjectNotFoundException,
    HotelNotFoundHTTPException,
    HotelNotFoundException,
)
from src.schemas.hotels import HotelPATCH, HotelAdd
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
@cache(expire=30)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Адресс отеля"),
    data_from: date = Query(example="2026-04-17"),
    data_to: date = Query(example="2026-04-25"),
):
    return await HotelService(db).get_filtered_by_time(
        pagination, title, location, data_from, data_to
    )


@router.get("/{hotel_id}", summary="Получаем отель по ID")
@cache(expire=30)
async def get_hotel_from_id(
    hotel_id: int,
    db: DBDep,
):
    try:
        return await HotelService(db).get_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Тест 1(СОЧИ)",
                "value": {"title": "Отлель у моря", "location": "Royal OAK"},
            },
            "2": {
                "summary": "Тест 2(ОАЭ)",
                "value": {"title": "Пальма Beach", "location": "Audemar Pigue"},
            },
        }
    ),
):

    add_hotel_stmt = await HotelService(db).add_hotel(hotel_data)
    return {"status": "OK", "data": add_hotel_stmt}


@router.put("/{hotel_id}")
async def update_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    db: DBDep,
):
    try:
        await HotelService(db).update_hotel(hotel_id, hotel_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Чуть-Чуть меняем данные",
    description="Капец обновляем данные об отеле и потом мы делаем то и может быть потмо не это просто нужно заполнить что-то",
)
async def partially_update_hotel(
    hotel_id: int,
    hotel_data: HotelPATCH,
    db: DBDep,
):
    try:
        await HotelService(db).partially_update_hotel(hotel_id, hotel_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}


@router.delete("/hotels/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    db: DBDep,
):
    try:
        await HotelService(db).delete_hotel(hotel_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}
