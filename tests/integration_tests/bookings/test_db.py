from datetime import date

from src.schemas.bookings import BookingAdd


# CREATE READ UPDATE DELETE
async def test_booking_crud(db):
    # CREATE
    room_id = (await db.rooms.get_all())[0].id
    user_id = (await db.users.get_all())[0].id
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        price=20_000,
        data_from=date(year=2026, month=9, day=1),
        data_to=date(year=2026, month=9, day=15),
    )
    booking = await db.bookings.add(booking_data)

    # READ
    book = await db.bookings.get_one_or_none(id=booking.id)
    assert book
    assert book.id == booking.id
    assert book.user_id == booking_data.user_id

    # UPDATE
    new_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        price=100_000,
        data_from=date(year=2026, month=9, day=1),
        data_to=date(year=2026, month=10, day=15),
    )
    await db.bookings.edit(new_data, True, id=booking.id)
    updated_booking = await db.bookings.get_one_or_none(id=booking.id)
    assert updated_booking
    assert updated_booking.id == booking.id
    assert updated_booking.price == 100_000

    # DELETE
    await db.bookings.delete(id=booking.id)
    book = await db.bookings.get_one_or_none(id=booking.id)
    assert not book
