import pytest

from src.schemas.hotels import HotelAdd

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_add_hotel(db):
    hotel_add = HotelAdd(title="Крутой отель", location="Абу Даби")
    await db.hotels.add(hotel_add)
    await db.commit()
