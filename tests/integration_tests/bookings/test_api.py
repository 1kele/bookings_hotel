import pytest


@pytest.mark.parametrize(
    "room_id, data_from, data_to, status_code",
    [
        (1, "2026-04-01", "2026-04-10", 200),
        (1, "2026-04-02", "2026-04-12", 200),
        (1, "2026-04-03", "2026-04-13", 200),
        (1, "2026-04-04", "2026-04-14", 200),
        (1, "2026-04-04", "2026-04-14", 200),
        (1, "2026-04-06", "2026-04-16", 500),
    ],
)
async def test_add_booking(room_id, data_from, data_to, status_code, authenticate_ac):
    result = await authenticate_ac.post(
        "/bookings",
        json={"room_id": room_id, "data_from": data_from, "data_to": data_to},
    )
    assert result.status_code == status_code
    if status_code == 200:
        res = result.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.fixture(scope="session")
async def clear_all_bookings(db):
    await db.bookings.delete()
    await db.commit()


@pytest.mark.parametrize(
    "room_id, data_from, data_to, count",
    [
        (1, "2026-04-01", "2026-04-10", 1),
        (1, "2026-04-02", "2026-04-12", 2),
        (1, "2026-04-03", "2026-04-13", 3),
    ],
)
async def test_add_and_get_my_bookings(
    clear_all_bookings, room_id, data_from, data_to, count, authenticate_ac
):
    result = await authenticate_ac.post(
        "/bookings",
        json={"room_id": room_id, "data_from": data_from, "data_to": data_to},
    )

    res_ = await authenticate_ac.get("/bookings/me")
    all_my_bookings = res_.json()["data"]
    last_booking = all_my_bookings[-1]

    assert result.status_code == 200
    assert res_.status_code == 200
    assert len(all_my_bookings) == count
    assert last_booking["room_id"] == room_id
    assert last_booking["data_from"] == data_from
    assert last_booking["data_to"] == data_to
    assert "id" in last_booking
    assert "price" in last_booking
