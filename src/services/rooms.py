from datetime import date

from src.exceptions import (
    check_date_to_after_date_from,
    ObjectNotFoundException,
    RoomNotFoundException,
)
from src.schemas.facilities import RoomsFacilityAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequesst, RoomPatch, Room
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def get_rooms_filter_by_time(self, hotel_id: int, data_from: date, data_to: date):
        check_date_to_after_date_from(data_from, data_to)
        result = await self.db.rooms.get_rooms_filter_by_time(
            hotel_id=hotel_id, data_from=data_from, data_to=data_to
        )
        return result

    async def get_one_room(self, room_id: int, hotel_id: int):
        return await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)

    async def check_room_exists(self, room_id: int):
        try:
            await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException as ex:
            raise RoomNotFoundException from ex

    async def create_room(self, hotel_id: int, data: RoomAddRequest) -> Room:
        await HotelService(self.db).check_hotel_exists(hotel_id)

        _room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump())
        room: Room = await self.db.rooms.add(_room_data)  # type: ignore

        rooms_facilities_data = [
            RoomsFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in data.facilities_ids
        ]
        if rooms_facilities_data:
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()

        return room

    async def update_room(self, hotel_id: int, room_id: int, data: RoomAddRequest):
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.check_room_exists(room_id)

        _room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump(exclude={"facilities_ids"}))

        await self.db.rooms_facilities.set_room_facilities(room_id, data.facilities_ids)
        await self.db.rooms.edit(_room_data, True, id=room_id)
        await self.db.commit()

    async def partially_update_room(self, hotel_id: int, room_id: int, data: RoomPatchRequesst):
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.check_room_exists(room_id)

        _room_data_check = data.model_dump(exclude_none=True)
        _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_check)

        await self.db.rooms.edit(_room_data, exclude_unset=True, hotel_id=hotel_id, id=room_id)

        if "facilities_ids" in _room_data_check and data.facilities_ids is not None:
            await self.db.rooms_facilities.set_room_facilities(room_id, data.facilities_ids)

        await self.db.commit()

    async def delete_room(self, hotel_id: int, room_id: int):
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.check_room_exists(room_id)
        await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
        await self.db.commit()
