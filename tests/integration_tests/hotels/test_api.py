async def test_get_hotels(ac):
    responce = await ac.get("/hotels", params={"data_from": "2026-04-17", "data_to": "2026-04-27"})
    print(f"{responce.status_code}")

    assert responce.status_code == 200
