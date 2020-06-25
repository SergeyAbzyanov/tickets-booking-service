from typing import List
from sqlalchemy import and_

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db import db, Cinema, CinemaHall, FilmShow
from src.routers.cinema_hall import CinemaHallOut
from src.routers.film_show import FilmShowOut

router = APIRouter()


class CinemaIn(BaseModel):
    name: str
    city: str


class CinemaInUpdate(BaseModel):
    name: str = None
    city: str = None


class CinemaOut(BaseModel):
    id: int
    name: str
    city: str

    @classmethod
    def from_model(cls, m: Cinema):
        return cls(id=m.id, name=m.name, city=m.city,)


class CinemaHallIn(BaseModel):
    name: str
    rows: int
    places_in_row: int


@router.get("/", response_model=List[CinemaOut])
async def get_cinema_list():
    async with db.transaction():
        cinema_list = await Cinema.query.order_by(Cinema.id).gino.all()
        cinema_list = [CinemaOut.from_model(cinema) for cinema in cinema_list]
        return cinema_list


@router.post("/", response_model=CinemaOut)
async def create_cinema(cinema_in: CinemaIn):
    cinema = await Cinema.create(name=cinema_in.name, city=cinema_in.city)
    return CinemaOut.from_model(cinema)


@router.get("/{cinema_id}", response_model=CinemaOut)
async def get_cinema(cinema_id: int):
    cinema = await Cinema.query.where(Cinema.id == cinema_id).gino.first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Cinema not found")
    return CinemaOut.from_model(cinema)


@router.patch("/{cinema_id}")
async def update_cinema(cinema_id: int, cinema_in: CinemaInUpdate):
    cinema = await Cinema.query.where(Cinema.id == cinema_id).gino.first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Cinema not found")
    if cinema_in.name:
        await cinema.update(name=cinema_in.name).apply()
    if cinema_in.city:
        await cinema.update(city=cinema_in.city).apply()
    return "Updated"


@router.post("/{cinema_id}/hall/", response_model=CinemaHallOut)
async def create_cinema_hall(cinema_id: int, cinema_hall_in: CinemaHallIn):
    cinema = await Cinema.query.where(Cinema.id == cinema_id).gino.first()
    if not cinema:
        raise HTTPException(
            status_code=404, detail="Cinema ID for new cinema hall not found"
        )
    cinema_hall = await CinemaHall.create(
        name=cinema_hall_in.name,
        id_cinema=cinema_id,
        rows=cinema_hall_in.rows,
        places_in_row=cinema_hall_in.places_in_row,
    )
    return CinemaHallOut.from_model(cinema_hall)


@router.get("/{cinema_id}/hall/", response_model=List[CinemaHallOut])
async def get_cinema_hall_list(cinema_id: int):
    async with db.transaction():
        cinema_hall_list = await CinemaHall.query.where(
            CinemaHall.id_cinema == cinema_id
        ).gino.all()
        cinema_hall_list = [
            CinemaHallOut.from_model(cinema) for cinema in cinema_hall_list
        ]
        return cinema_hall_list


@router.get("/{cinema_id}/hall/{cinema_hall_id}", response_model=CinemaHallOut)
async def get_cinema_hall(cinema_id: int, cinema_hall_id: int):
    async with db.transaction():
        cinema_hall = await CinemaHall.query.where(
            and_(CinemaHall.id == cinema_hall_id, CinemaHall.id_cinema == cinema_id)
        ).gino.first()
        if not cinema_hall:
            raise HTTPException(status_code=404, detail="Cinema hall not found")
        return CinemaHallOut.from_model(cinema_hall)


@router.get(
    "/{cinema_id}/hall/{cinema_hall_id}/film-show/", response_model=List[FilmShowOut]
)
async def get_film_show_list(cinema_id: int, cinema_hall_id: int):
    async with db.transaction():
        cinema = await Cinema.query.where(Cinema.id == cinema_id).gino.first()
        if not cinema:
            raise HTTPException(status_code=404, detail="Cinema not found")
        cinema_hall = await CinemaHall.query.where(
            and_(CinemaHall.id == cinema_hall_id, CinemaHall.id_cinema == cinema_id)
        ).gino.first()
        if not cinema_hall:
            raise HTTPException(status_code=404, detail="Cinema hall not found")
        film_show = await FilmShow.query.where(
            FilmShow.id_hall == cinema_hall.id
        ).gino.all()
        if not film_show:
            raise HTTPException(status_code=404, detail="Film show not found")
        film_show_list = [FilmShowOut.from_model(show) for show in film_show]
        return film_show_list
