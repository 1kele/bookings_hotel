from datetime import date

from sqlalchemy import select, func

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


def rooms_ids_for_booking(
    data_from: date,
    data_to: date,
    hotel_id: int | None = None,
):
    rooms_booked = (
        select(BookingsOrm.room_id, func.count("*").label("booking_count"))
        .select_from(BookingsOrm)
        .filter(BookingsOrm.data_from <= data_to, BookingsOrm.data_to >= data_from)
        .group_by(BookingsOrm.room_id)
        .cte(name="rooms_booked")
    )

    whole_table = (
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(rooms_booked.c.booking_count, 0)).label(
                "avaliable_num_of_rooms"
            ),
        )
        .select_from(RoomsOrm)
        .outerjoin(rooms_booked, RoomsOrm.id == rooms_booked.c.room_id)
        .cte(name="whole_table")
    )

    rooms_ids_for_hotels = select(RoomsOrm.id).select_from(RoomsOrm)

    if hotel_id:
        rooms_ids_for_hotels.filter_by(hotel_id=hotel_id)

    query = (
        select(whole_table.c.room_id)
        .select_from(whole_table)
        .filter(
            whole_table.c.avaliable_num_of_rooms > 0,
            whole_table.c.room_id.in_(rooms_ids_for_hotels),
        )
    )

    return query
