from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload, joinedload

from src.exceptions import RoomNotFoundException
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepositories
from src.repositories.mappers.mappers import RoomDataMapper, RoomWithRelsDataMapper
from src.repositories.utils import rooms_ids_for_booking


class RoomsRepository(BaseRepositories):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_rooms_filter_by_time(self, hotel_id: int, data_from: date, data_to: date):
        rooms_ids_to_get = rooms_ids_for_booking(data_from, data_to, hotel_id)

        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        result = await self.session.execute(query)
        return [
            RoomWithRelsDataMapper.map_to_domain_entity(model)
            for model in result.unique().scalars().all()
        ]

    async def get_one_with_rels(self, **filter_by):
        query = (
            select(self.model).options(selectinload(self.model.facilities)).filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise RoomNotFoundException

        return RoomWithRelsDataMapper.map_to_domain_entity(model)
