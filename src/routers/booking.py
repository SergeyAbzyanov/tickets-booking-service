from typing import List

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db import db, Booking, FilmShow
from datetime import datetime

router = APIRouter()


class BookingIn(BaseModel):
    id_film_show: int
    row: int
    place: int


class BookingOut(BaseModel):
    id: int
    id_film_show: int
    row: int
    place: int

    @classmethod
    def from_model(cls, m: Booking):
        return cls(id=m.id, id_film_show=m.id_film_show, row=m.row, place=m.place,)


@router.get("/", response_model=List[BookingOut])
async def get_booking_list():
    async with db.transaction():
        booking_list = await Booking.query.order_by(Booking.id).gino.all()
        booking_list = [BookingOut.from_model(booking) for booking in booking_list]
        return booking_list


@router.post("/", response_model=BookingOut)
async def create_booking(booking_in: BookingIn):
    now = datetime.now()
    film_show = await FilmShow.query.where(
        FilmShow.id == booking_in.id_film_show
    ).gino.first()
    if now >= film_show.start_time:
        raise HTTPException(status_code=400, detail="This film show already gone")
    try:
        booking = await Booking.create(
            id_film_show=booking_in.id_film_show,
            row=booking_in.row,
            place=booking_in.place,
        )
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="This place already busy")
    return BookingOut.from_model(booking)


@router.get("/{id_booking}", response_model=BookingOut)
async def get_booking(id_booking: int):
    booking = await Booking.query.where(Booking.id == id_booking).gino.first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingOut.from_model(booking)


@router.delete("/{id_booking}")
async def delete_booking(id_booking: int):
    booking = await Booking.query.where(Booking.id == id_booking).gino.first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    await Booking.delete.where(Booking.id == id_booking).gino.status()
