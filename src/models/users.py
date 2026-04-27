import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]

    last_name: Mapped[str]
    first_name: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")
    created_at: Mapped[datetime.date] = mapped_column(server_default=func.now())
