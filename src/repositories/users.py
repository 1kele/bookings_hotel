from sqlalchemy import select

from src.models.users import UsersOrm
from src.repositories.base import BaseRepositories
from src.repositories.mappers.mappers import (
    UserDataMapper,
    UserWithHashedPasswordDataMapper,
)


class UsersRepository(BaseRepositories):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, username: str):
        query = select(self.model).filter_by(username=username)
        result = await self.session.execute(query)
        model = result.scalars().one()
        return UserWithHashedPasswordDataMapper.map_to_domain_entity(model)
