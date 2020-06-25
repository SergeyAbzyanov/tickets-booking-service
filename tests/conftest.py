import pytest

from src.db import Cinema, CinemaHall, Film, FilmShow, Booking, init_db, close_db


@pytest.fixture(scope="function", autouse=True)
async def clean_db_records():
    await init_db()
    await Booking.delete.gino.status()
    await FilmShow.delete.gino.status()
    await CinemaHall.delete.gino.status()
    await Cinema.delete.gino.status()
    await Film.delete.gino.status()
    await close_db()
    yield
