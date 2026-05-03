from sqlalchemy import select
from typing import cast

from src.models.users import UsersOrm
from src.repositories.base import BaseRepositories
from src.repositories.mappers.mappers import (
    UserDataMapper,
    UserWithHashedPasswordDataMapper,
)
from src.schemas.users import UserWithHashedPassword


class UsersRepository(BaseRepositories):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, username: str) -> UserWithHashedPassword:
        query = select(self.model).filter_by(username=username)
        result = await self.session.execute(query)
        model = result.scalars().one()
        return cast(
            UserWithHashedPassword, UserWithHashedPasswordDataMapper.map_to_domain_entity(model)
        )
