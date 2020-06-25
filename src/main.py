from fastapi import FastAPI
from .routers import cinema, cinema_hall, film, film_show, booking

from .db import init_db, close_db

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    await close_db()


app.include_router(cinema.router, prefix="/cinema")
app.include_router(cinema_hall.router, prefix="/cinema-hall")
app.include_router(film.router, prefix="/film")
app.include_router(film_show.router, prefix="/film-show")
app.include_router(booking.router, prefix="/booking")
