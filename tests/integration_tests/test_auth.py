from src.services.auth import Authentication


def test_encode_and_decode_access_token():
    data = {"user_id": 1}

    jwt_token = Authentication().create_access_token(data)
    jwt_decoded = Authentication().decode_token(jwt_token)

    assert jwt_decoded
    assert jwt_decoded.get("user_id") == data["user_id"]
