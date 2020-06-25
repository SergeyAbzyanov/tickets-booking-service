from typing import List
from sqlalchemy import and_, or_

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db import db, FilmShow, Film
from datetime import datetime, date, time, timedelta

DAY_END_TIME = time(7, 0)

router = APIRouter()


class FilmShowIn(BaseModel):
    start_time: str
    id_hall: int
    id_film: int


class FilmShowInUpdate(BaseModel):
    id_hall: int = None
    id_film: int = None


class FilmShowOut(BaseModel):
    id: int
    show_date: date
    start_time: time
    end_time: time
    id_hall: int
    id_film: int

    @classmethod
    def from_model(cls, m: FilmShow):
        return cls(
            id=m.id,
            show_date=m.show_date,
            start_time=m.start_time.time(),
            end_time=m.end_time.time(),
            id_hall=m.id_hall,
            id_film=m.id_film,
        )


def validate_date(check_date):
    if check_date:
        try:
            check_date = datetime.strptime(check_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Incorrect date format")
    return check_date


@router.get("/", response_model=List[FilmShowOut])
async def get_film_show_list(start_date: str = None, end_date: str = None):
    start_date, end_date = validate_date(start_date), validate_date(end_date)
    async with db.transaction():
        query = FilmShow.query
        if start_date:
            query = query.where(
                FilmShow.start_time >= datetime.combine(start_date, DAY_END_TIME)
            )
        if end_date:
            query = query.where(
                FilmShow.end_time
                < datetime.combine(end_date + timedelta(days=1), DAY_END_TIME)
            )
        film_show_list = await query.order_by(FilmShow.id).gino.all()
        film_show_list = [
            FilmShowOut.from_model(film_show) for film_show in film_show_list
        ]
        return film_show_list


@router.post("/", response_model=FilmShowOut)
async def create_film_show(film_show_in: FilmShowIn):
    start_time = datetime.fromisoformat(film_show_in.start_time.strip("Zz"))
    film = await Film.query.where(Film.id == film_show_in.id_film).gino.first()
    duration = film.duration
    end_time = start_time + timedelta(minutes=duration)

    # Split date and time
    show_date = start_time.date()
    film_show_time_conflict = await FilmShow.query.where(
        or_(
            and_(start_time <= FilmShow.start_time, FilmShow.start_time <= end_time),
            and_(start_time <= FilmShow.end_time, FilmShow.end_time <= end_time),
        )
    ).gino.first()
    if film_show_time_conflict:
        raise HTTPException(status_code=400, detail="Show time already busy")

    film_show = await FilmShow.create(
        show_date=show_date,
        start_time=start_time,
        end_time=end_time,
        id_hall=film_show_in.id_hall,
        id_film=film_show_in.id_film,
    )
    return FilmShowOut.from_model(film_show)


@router.get("/{film_show_id}", response_model=FilmShowOut)
async def get_film_show(film_show_id: int):
    film_show = await FilmShow.query.where(FilmShow.id == film_show_id).gino.first()
    if not film_show:
        raise HTTPException(status_code=404, detail="Film not found")
    return FilmShowOut.from_model(film_show)


@router.delete("/{film_show_id}")
async def delete_film_show(film_show_id: int):
    film_show = await FilmShow.query.where(FilmShow.id == film_show_id).gino.first()
    if not film_show:
        raise HTTPException(status_code=404, detail="Film_show not found")
    await FilmShow.delete.where(FilmShow.id == film_show_id).gino.status()
