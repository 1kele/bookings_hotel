from sqlalchemy import delete, select, insert

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepositories
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import RoomsFacility


class FacilitiesRepositories(BaseRepositories):
    model = FacilitiesOrm
    mapper = FacilityDataMapper


class RoomsFacilitiesRepositories(BaseRepositories):
    model = RoomsFacilitiesOrm
    schema = RoomsFacility

    async def set_room_facilities(self, room_id: int, facilities_ids: list[int]):
        query = select(self.model.facility_id).filter_by(room_id=room_id)  # type: ignore
        res = await self.session.execute(query)
        current_facilities_ids = res.scalars().all()
        ids_to_delete = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_append = list(set(facilities_ids) - set(current_facilities_ids))

        if ids_to_delete:
            delete_stmt = delete(self.model).filter(
                self.model.facility_id.in_(ids_to_delete),
                self.model.room_id == room_id,  # type: ignore
            )
            await self.session.execute(delete_stmt)

        if ids_to_append:
            append_stmt = insert(self.model).values(
                [{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_append]
            )
            await self.session.execute(append_stmt)
