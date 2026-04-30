from fastapi import Response

from src.api.dependencies import UserIdDep
from src.exceptions import UserNotExistException, WrongPasswordException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import Authentication
from src.services.base import BaseService


class AuthenticationService(BaseService):
    async def register(self, data: UserRequestAdd):
        hashed_password = Authentication().hash_password(data.password)
        new_user_data = UserAdd(
            email=data.email,
            username=data.username,
            last_name=data.last_name,
            first_name=data.first_name,
            hashed_password=hashed_password,
        )
        await self.db.users.add(new_user_data)
        await self.db.commit()

    async def login(self, response: Response, data: UserRequestAdd):
        user = await self.db.users.get_user_with_hashed_password(data.username)
        await self.db.commit()

        if not user:
            raise UserNotExistException

        verif_password = Authentication().verify_password(data.password, user.hashed_password)
        if not verif_password:
            raise WrongPasswordException

        access_token = Authentication().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)

        return access_token

    async def get_me(self, user_id: UserIdDep):
        user = await self.db.users.get_one(id=user_id)
        return user

    async def logout(
        self,
        response: Response,
    ):
        response.delete_cookie("access_token")
