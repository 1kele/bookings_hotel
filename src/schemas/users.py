from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserRequestAdd(BaseModel):
    email: EmailStr
    username: str
    last_name: str
    first_name: str
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    username: str
    last_name: str
    first_name: str
    hashed_password: str


class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    last_name: str
    first_name: str
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserWithHashedPassword(User):
    hashed_password: str
