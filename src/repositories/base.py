import logging

from typing import Sequence, ClassVar
from asyncpg import UniqueViolationError
from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.database import Base
from src.exceptions import ObjectNotFoundException, UserAlreadyExistException
from src.repositories.mappers.base import DataMapper


class BaseRepositories:
    model: ClassVar[type[Base]]
    mapper: ClassVar[type[DataMapper]]

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *arg):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        query = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(query)
        except IntegrityError as ex:
            if ex.orig and isinstance(ex.orig.__cause__, UniqueViolationError):
                raise UserAlreadyExistException from ex
            logging.error(
                f"Незнакомая ошибка, тип ошибки: {type(ex.orig.__cause__ if ex.orig else None)}, входные данные: {data}"
            )
            raise ex

        return self.mapper.map_to_domain_entity(result.scalars().one())

    async def add_bulk(self, data: Sequence[BaseModel]):
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def delete(self, **filter_by):
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)
