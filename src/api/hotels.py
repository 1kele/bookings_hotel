from datetime import date

from fastapi import Query, APIRouter, Body, HTTPException

from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.schemas.hotels import HotelPATCH, HotelAdd

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
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        data_from=data_from,
        data_to=data_to,
        title=title,
        location=location,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
    )


@router.get("/{hotel_id}", summary="Получаем отель по ID")
@cache(expire=30)
async def get_hotel_from_id(
    hotel_id: int,
    db: DBDep,
):
    current_hotel = await db.hotels.get_one_or_none(id=hotel_id)
    await db.commit()
    if not current_hotel:
        raise HTTPException(status_code=404, detail="Отель не найден")
    return current_hotel


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

    add_hotel_stmt = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "data": add_hotel_stmt}


@router.put("/{hotel_id}")
async def update_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    db: DBDep,
):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
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
    await db.hotels.edit_exact(hotel_data, True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/hotels/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    db: DBDep,
):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}
