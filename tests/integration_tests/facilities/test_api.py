async def test_get_facility(ac):
    responce = await ac.get("/facilities")

    assert responce.status_code == 200


async def test_add_facility(ac):
    facility_title = "FREE WI-FI"
    responce = await ac.post("/facilities", json={"title": "FREE WI-FI"})
    res = responce.json()
    print(res)
    assert res["data"]["title"] == facility_title
    assert isinstance(res, dict)
    assert responce.status_code == 200
