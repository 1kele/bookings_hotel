import bcrypt
import jwt

from datetime import datetime, timezone, timedelta

from fastapi import HTTPException

from src.config import settings
from src.services.base import BaseService


class Authentication(BaseService):
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain_password, hashed_password):
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Токен истек")
        except jwt.exceptions.InvalidSignatureError:
            raise HTTPException(status_code=401, detail="Неверный токен")
