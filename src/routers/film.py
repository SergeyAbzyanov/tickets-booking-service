from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db import db, Film

router = APIRouter()


class FilmIn(BaseModel):
    title: str
    genre: str
    cast: str
    description: str
    duration: int


class FilmInUpdate(BaseModel):
    title: str = None
    genre: str = None
    cast: str = None
    description: str = None
    duration: int = None


class FilmOut(BaseModel):
    id: int
    title: str
    genre: str
    cast: str
    description: str
    duration: int

    @classmethod
    def from_model(cls, m: Film):
        return cls(
            id=m.id,
            title=m.title,
            genre=m.genre,
            cast=m.cast,
            description=m.description,
            duration=m.duration,
        )


@router.get("/", response_model=List[FilmOut])
async def get_film_list():
    async with db.transaction():
        film_list = await Film.query.order_by(Film.id).gino.all()
        film_list = [FilmOut.from_model(film) for film in film_list]
        return film_list


@router.post("/", response_model=FilmOut)
async def create_film(film_in: FilmIn):
    film = await Film.create(
        title=film_in.title,
        genre=film_in.genre,
        cast=film_in.cast,
        description=film_in.description,
        duration=film_in.duration,
    )
    return FilmOut.from_model(film)


@router.get("/{film_id}", response_model=FilmOut)
async def get_film(film_id: int):
    film = await Film.query.where(Film.id == film_id).gino.first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return FilmOut.from_model(film)


@router.patch("/{film_id}")
async def update_film(film_id: int, film_in: FilmInUpdate):
    film = await Film.query.where(Film.id == film_id).gino.first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    await film.update(**film_in.dict(exclude_unset=True)).apply()
