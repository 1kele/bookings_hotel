# ruff: noqa: E402
import json
import pytest
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

from src.config import settings
from src.database import Base, async_session_maker, engine
from src.main import app
from httpx import ASGITransport, AsyncClient

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
async def check_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session")
async def db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_mode, db):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open("tests/mock_rooms.json", encoding="utf-8") as f:
        data_rooms = json.load(f)
    with open("tests/mock_hotels.json", encoding="utf-8") as f:
        data_hotels = json.load(f)

    hotel = [HotelAdd.model_validate(hotel) for hotel in data_hotels]
    room = [RoomAdd.model_validate(room) for room in data_rooms]

    await db.hotels.add_bulk(hotel)
    await db.rooms.add_bulk(room)
    await db.commit()


@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    await ac.post(
        "/auth/register",
        json={
            "email": "kot@pes.com",
            "username": "kot",
            "last_name": "Petr",
            "first_name": "Ivanov",
            "password": "AWQ2281337",
        },
    )


@pytest.fixture(scope="session")
async def authenticate_ac(register_user, ac):
    await ac.post(
        "/auth/login",
        json={
            "email": "kot@pes.com",
            "username": "kot",
            "last_name": "Petr",
            "first_name": "Ivanov",
            "password": "AWQ2281337",
        },
    )

    assert ac.cookies["access_token"]
    yield ac
