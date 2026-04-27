import pytest


@pytest.mark.parametrize(
    "email, username, last_name, first_name, password, status_code",
    [
        ("kotenok@pes.com", "AWQ", "Irina", "Ibragimova", "123123", 200),
        ("prokofiev@mail.com", "besmila", "Konstantin", "Ivamovich", "qweqwe", 200),
        ("baraban@gmail.com", "qwerty", "Kirill", "Krigger", "balala", 200),
        ("sdfasdf", "qwertssy", "Kirilsal", "Krigager", "baladla", 422),
        ("sdfasdf@sadf", "qwertsassy", "Kisrilsal", "sKrigager", "baaladla", 422),
    ],
)
async def test_whole_sequence_auth(
    email: str,
    username: str,
    last_name: str,
    first_name: str,
    password: str,
    status_code: int,
    ac,
):
    registed_user = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "last_name": last_name,
            "first_name": first_name,
            "password": password,
        },
    )

    assert registed_user.status_code == status_code
    if status_code == 200:
        await ac.post(
            "/auth/login",
            json={
                "email": email,
                "username": username,
                "last_name": last_name,
                "first_name": first_name,
                "password": password,
            },
        )

        assert ac.cookies["access_token"]

        get_current_user = await ac.get("/auth/me")
        current_user = get_current_user.json()
        assert current_user["data"]["email"] == email
        assert current_user["data"]["username"] == username
        assert current_user["data"]["first_name"] == first_name
        assert current_user["data"]["last_name"] == last_name

        logout_user = await ac.post("/auth/logout")

        assert logout_user.status_code == status_code
        assert "access_token" not in ac.cookies

        get_empty_user = await ac.get("/auth/me")
        assert get_empty_user.status_code == 401
