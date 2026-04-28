from datetime import date

from fastapi import HTTPException


class NeglezheExceptions(Exception):
    detail = "Неизвестная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, args, **kwargs)


class ObjectNotFoundException(NeglezheExceptions):
    detail = "Объект не найден"

class RoomNotFoundException(NeglezheExceptions):
    detail = "Номер не найден"

class HotelNotFoundException(NeglezheExceptions):
    detail = "Отель не найден"

class AllRoomsAreBookedException(NeglezheExceptions):
    detail = "Не осталось свободных номеров"


class UserAlreadyExistException(NeglezheExceptions):
    detail = "Такой пользователь уже существует"

class UserNotExistException(NeglezheExceptions):
    detail = "Такой пользователь не существует"

class WrongPasswordException(NeglezheExceptions):
    detail = "Такой пользователь не существует"

def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_from >= date_to:
        raise HTTPException(status_code=422, detail="Дата заезда не может быть позже даты выезда")


class NeglezheHTTPExceptions(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundHTTPException(NeglezheHTTPExceptions):
    status_code = 404
    detail = "Отель не найден"


class RoomNotFoundHTTPException(NeglezheHTTPExceptions):
    status_code = 404
    detail = "Номер не найден"

class UserAlreadyExistHTTPException(NeglezheHTTPExceptions):
    status_code = 409
    detail = "Такой пользователь уже существует"


class UserNotExistHTTPException(NeglezheHTTPExceptions):
    status_code = 404
    detail = "Такой пользователь не существует"


class WrongPasswordHTTPException(NeglezheHTTPExceptions):
    status_code = 409
    detail = "Неправильный пароль"