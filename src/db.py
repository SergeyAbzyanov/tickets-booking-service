from gino import Gino
from .settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

db = Gino()


class Cinema(db.Model):
    __tablename__ = "cinema"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), nullable=False)
    city = db.Column(db.Unicode(), nullable=False)


class CinemaHall(db.Model):
    __tablename__ = "hall"

    id = db.Column(db.Integer(), primary_key=True)
    id_cinema = db.Column("id_cinema", None, db.ForeignKey("cinema.id"))
    name = db.Column(db.Unicode(), nullable=False)
    rows = db.Column(db.Integer(), nullable=False)
    places_in_row = db.Column(db.Integer(), nullable=False)


class Film(db.Model):
    __tablename__ = "films"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Unicode(), nullable=False)
    genre = db.Column(db.Unicode(), nullable=False)
    cast = db.Column(db.Unicode(), nullable=False)
    description = db.Column(db.Unicode(), nullable=False)
    duration = db.Column(db.Integer(), nullable=False)


class FilmShow(db.Model):
    """
    Таблица сеансы привязана в кинозалу и к фильму.
    Аттрибуты - время начала (при создании), время окончания (авто), дата.
    При создании нужно проверять что не пересекается с другим сеансом.
    Изменять нельзя, можно только удалить
    """

    __tablename__ = "film_show"

    id = db.Column(db.Integer(), primary_key=True)
    show_date = db.Column(db.Date())
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    id_hall = db.Column("id_hall", None, db.ForeignKey("hall.id"))
    id_film = db.Column("id_film", None, db.ForeignKey("films.id"))


class Booking(db.Model):
    """
    Таблица забронированное место в сеансе.
    Сеанс, ряд и место (unique key constraint)
    """

    __tablename__ = "booking"

    id = db.Column(db.Integer(), primary_key=True)
    id_film_show = db.Column("id_film_show", None, db.ForeignKey("film_show.id"))
    row = db.Column(db.Integer(), nullable=False)
    place = db.Column(db.Integer(), nullable=False)

    _idx = db.Index(
        "booking_idx_film_show_row_place", "id_film_show", "row", "place", unique=True
    )


async def init_db():
    await db.set_bind(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    # Create tables
    await db.gino.create_all()


async def close_db():
    engine, db.bind = db.bind, None
    await engine.close()
