from fastapi import Query, Depends, Request, HTTPException
from typing import Annotated
from pydantic import BaseModel

from src.database import async_session_maker
from src.services.auth import Authentication
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[int, Query(1, description="Номер страницы", ge=1)]
    per_page: Annotated[
        int | None, Query(None, description="Количество на одной странице", ge=1, lt=30)
    ]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token", None)
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не продоставили токен доступа")
    return access_token


def get_current_user_id(access_token: str = Depends(get_token)):
    data = Authentication().decode_token(access_token)
    user_id = data.get("user_id", None)
    return user_id


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
