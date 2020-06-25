from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db import db, Cinema, CinemaHall

router = APIRouter()


class CinemaHallInUpdate(BaseModel):
    name: str = None
    rows: int = None
    places_in_row: int = None


class CinemaHallOut(BaseModel):
    id: int
    name: str
    id_cinema: int
    rows: int
    places_in_row: int

    @classmethod
    def from_model(cls, m: CinemaHall):
        return cls(
            id=m.id,
            name=m.name,
            id_cinema=m.id_cinema,
            rows=m.rows,
            places_in_row=m.places_in_row,
        )


@router.get("/", response_model=List[CinemaHallOut])
async def get_cinema_hall_list():
    async with db.transaction():
        cinema_hall_list = await CinemaHall.query.order_by(CinemaHall.id).gino.all()
        cinema_hall_list = [
            CinemaHallOut.from_model(cinema) for cinema in cinema_hall_list
        ]
        return cinema_hall_list


@router.get("/{cinema_hall_id}", response_model=CinemaHallOut)
async def get_cinema_hall(cinema_hall_id: int):
    cinema_hall = await CinemaHall.query.where(
        CinemaHall.id == cinema_hall_id
    ).gino.first()
    if not cinema_hall:
        raise HTTPException(status_code=404, detail="Cinema hall not found")
    return CinemaHallOut.from_model(cinema_hall)


@router.patch("/{cinema_hall_id}")
async def update_cinema_hall(cinema_hall_id: int, cinema_hall_in: CinemaHallInUpdate):
    cinema_hall = await CinemaHall.query.where(
        CinemaHall.id == cinema_hall_id
    ).gino.first()
    if not cinema_hall:
        raise HTTPException(status_code=404, detail="Cinema hall not found")
    await cinema_hall.update(**cinema_hall_in.dict(exclude_unset=True)).apply()
    return "Updated"
