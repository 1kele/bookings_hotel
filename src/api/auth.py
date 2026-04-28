from fastapi import APIRouter, HTTPException, Response, Body

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import UserAlreadyExistException, UserAlreadyExistHTTPException, WrongPasswordHTTPException, \
    WrongPasswordException, UserNotExistHTTPException, UserNotExistException, ObjectNotFoundException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import Authentication
from src.services.auths import AuthenticationService

router = APIRouter(prefix="/auth", tags=["Аунтефикация и Авторизация"])


@router.post("/register")
async def register(data: UserRequestAdd, db: DBDep):
    try:
        await AuthenticationService(db).register(data)
    except UserAlreadyExistException:
        raise UserAlreadyExistHTTPException
    return {"status": "Ok"}


@router.post("/login")
async def login(
    response: Response,
    db: DBDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "user@example.com",
                "value": {
                    "email": "user@example.com",
                    "username": "string",
                    "last_name": "string",
                    "first_name": "string",
                    "password": "string",
                },
            },
            "2": {
                "summary": "baltin2803@mail.ru",
                "value": {
                    "email": "baltin2803@mail.ru",
                    "username": "1kele",
                    "last_name": "Baltin",
                    "first_name": "Mike",
                    "password": "password",
                },
            },
            "3": {
                "summary": "qwe@dude.com",
                "value": {
                    "email": "qwe@dude.com",
                    "username": "Bebra1122",
                    "last_name": "Nikita",
                    "first_name": "Luka",
                    "password": "qwerty",
                },
            },
        }
    ),
):
    try:
        access_token = await AuthenticationService(db).login(response, data)
    except UserNotExistException:
        raise UserNotExistHTTPException
    except WrongPasswordException:
        raise WrongPasswordHTTPException
    return {"access_token": access_token}


@router.get("/me")
async def get_me(user_id: UserIdDep, db: DBDep):
    user = await AuthenticationService(db).get_me(user_id)
    return {"data": user}


@router.post("/logout")
async def logout(response: Response, db: DBDep):
    await AuthenticationService(db).logout(response)
    return {"status": "ok"}
