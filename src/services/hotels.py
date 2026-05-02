from datetime import date

from src.api.dependencies import PaginationDep
from src.exceptions import (
    check_date_to_after_date_from,
    ObjectNotFoundException,
    HotelNotFoundException,
)
from src.schemas.hotels import HotelAdd, HotelPATCH
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_filtered_by_time(
        self,
        pagination: PaginationDep,
        title: str | None,
        location: str | None,
        data_from: date,
        data_to: date,
    ):
        per_page = pagination.per_page or 5
        check_date_to_after_date_from(data_from, data_to)
        return await self.db.hotels.get_filtered_by_time(
            data_from=data_from,
            data_to=data_to,
            title=title,
            location=location,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_hotel(
        self,
        hotel_id: int,
    ):
        return await self.db.hotels.get_one(id=hotel_id)

    async def add_hotel(self, hotel_data: HotelAdd):
        add_hotel_stmt = await self.db.hotels.add(hotel_data)
        await self.db.commit()
        return add_hotel_stmt

    async def update_hotel(self, hotel_id: int, hotel_data: HotelAdd):
        await self.check_hotel_exists(hotel_id)
        await self.db.hotels.edit(hotel_data, id=hotel_id)
        await self.db.commit()

    async def partially_update_hotel(self, hotel_id: int, hotel_data: HotelPATCH):
        await self.check_hotel_exists(hotel_id)
        await self.db.hotels.edit(hotel_data, True, id=hotel_id)
        await self.db.commit()

    async def delete_hotel(
        self,
        hotel_id: int,
    ):
        await self.check_hotel_exists(hotel_id)
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()

    async def check_hotel_exists(self, hotel_id: int):
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException
