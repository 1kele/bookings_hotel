from fastapi import APIRouter, HTTPException, Response, Body

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import UserAlreadyExistException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import Authentication

router = APIRouter(prefix="/auth", tags=["Аунтефикация и Авторизация"])


@router.post("/register")
async def register(data: UserRequestAdd, db: DBDep):
    hashed_password = Authentication().hash_password(data.password)
    new_user_data = UserAdd(
        email=data.email,
        username=data.username,
        last_name=data.last_name,
        first_name=data.first_name,
        hashed_password=hashed_password,
    )
    try:
        await db.users.add(new_user_data)
        await db.commit()
    except UserAlreadyExistException as ex:
        raise HTTPException(status_code=409, detail=ex.detail)

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
    user = await db.users.get_user_with_hashed_password(data.username)
    await db.commit()

    if not user:
        raise HTTPException(
            status_code=401, detail="Пользователь с такимми данными не зарегистрирован"
        )

    verif_password = Authentication().verify_password(data.password, user.hashed_password)
    if not verif_password:
        raise HTTPException(status_code=500, detail="Неверный пароль")

    access_token = Authentication().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(user_id: UserIdDep, db: DBDep):
    user = await db.users.get_one_or_none(id=user_id)
    await db.commit()
    return {"data": user}


@router.post("/logout")
async def logout(
    response: Response,
):
    response.delete_cookie("access_token")
    return {"status": "ok"}
