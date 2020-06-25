import datetime

from fastapi.testclient import TestClient
from src.main import app
from .create_functions import (
    create_film_show,
    preprocess_show_time,
    create_film_show_dependencies,
    create_film_show_with_dependencies,
)

DEFAULT_TIME = datetime.datetime.now() + datetime.timedelta(days=5)


def test_empty_list():
    with TestClient(app) as client:
        response = client.get("/film-show/")
        assert response.status_code == 200
        assert response.json() == []


def test_create():
    with TestClient(app) as client:
        # Create film show dependencies
        id_hall, id_film, film_duration = create_film_show_dependencies(
            client, return_duration=True
        )
        # Create film show
        film_show_data = {
            "start_time": DEFAULT_TIME.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "id_hall": id_hall,
            "id_film": id_film,
        }
        response = client.post("/film-show/", json=film_show_data)
        assert response.status_code == 200, response.json()
        film_show_data["id"] = response.json()["id"]
        # Preprocess time using start time and film duration
        preprocess_time = preprocess_show_time(DEFAULT_TIME, film_duration)
        for key in preprocess_time:
            film_show_data[key] = preprocess_time[key]
        assert response.json() == film_show_data


def test_list():
    with TestClient(app) as client:
        (
            id_cinema,
            id_hall,
            id_film,
            id_film_show,
            time,
        ) = create_film_show_with_dependencies(client, return_time=True)
        response = client.get("/film-show/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "show_date": time["show_date"],
                "start_time": time["start_time"],
                "end_time": time["end_time"],
                "id_hall": id_hall,
                "id_film": id_film,
                "id": id_film_show,
            }
        ]


def test_get():
    with TestClient(app) as client:
        (
            id_cinema,
            id_hall,
            id_film,
            id_film_show,
            time,
        ) = create_film_show_with_dependencies(client, return_time=True)
        response = client.get(f"/film-show/{id_film_show}")
        assert response.status_code == 200
        assert response.json() == {
            "show_date": time["show_date"],
            "start_time": time["start_time"],
            "end_time": time["end_time"],
            "id_hall": id_hall,
            "id_film": id_film,
            "id": id_film_show,
        }


def test_get_not_found():
    with TestClient(app) as client:
        # Check new film_show by id
        response = client.get(f"/film-show/{99}")
        assert response.status_code == 404


def test_create_show_time_conflict():
    with TestClient(app) as client:
        # Create film show dependencies
        id_hall, id_film = create_film_show_dependencies(client)
        # Create film shows to check show time conflict
        show_dt = datetime.datetime.now() + datetime.timedelta(hours=48)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        assert response.status_code == 200
        show_dt = datetime.datetime.now() + datetime.timedelta(hours=49)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        assert response.status_code == 400
        show_dt = datetime.datetime.now() + datetime.timedelta(hours=47)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        assert response.status_code == 400


def test_delete():
    with TestClient(app) as client:
        id_cinema, id_hall, id_film, id_film_show = create_film_show_with_dependencies(
            client
        )
        response = client.delete(f"/film-show/{id_film_show}")
        assert response.status_code == 200
        response = client.get(f"/film-show/{id_film_show}")
        assert response.status_code == 404


def test_delete_not_found():
    with TestClient(app) as client:
        response = client.delete(f"/film-show/{99}")
        assert response.status_code == 404


def test_create_show_time_overlaps_two_day_no_conflict():
    with TestClient(app) as client:
        # Create film show dependencies
        id_hall, id_film = create_film_show_dependencies(client)
        # Create film shows to check no conflict
        response, id_film_show = create_film_show(
            client, id_hall, id_film, DEFAULT_TIME
        )
        assert response.status_code == 200
        show_dt = DEFAULT_TIME + datetime.timedelta(days=2)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        assert response.status_code == 200


def test_create_show_time_overlaps_two_day_conflict():
    with TestClient(app) as client:
        # Create film show dependencies
        id_hall, id_film = create_film_show_dependencies(client)
        # Create film shows to check 2 days overlaps conflict
        show_dt = datetime.datetime(2020, 3, 3, 23, 50)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        assert response.status_code == 200
        show_dt = datetime.datetime(2020, 3, 4, 00, 20)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        assert response.status_code == 400


def test_filter_start_date():
    with TestClient(app) as client:
        # Current day + 5 days on 12:20
        first_show_start = datetime.datetime.combine(
            DEFAULT_TIME.date(), datetime.time(12, 20)
        )
        # Current day + 6 days on 12:20
        second_show_start = datetime.datetime.combine(
            DEFAULT_TIME.date() + datetime.timedelta(days=1), datetime.time(12, 20)
        )
        # Create first film show, no need to return any data
        create_film_show_with_dependencies(client, show_dt=first_show_start)
        # Create second film show, return data to check the filter by start date
        (
            id_cinema,
            id_hall,
            id_film,
            id_film_show,
            time,
        ) = create_film_show_with_dependencies(
            client, show_dt=second_show_start, return_time=True
        )
        # Check filter by start date, should return data of second film show
        query_date = second_show_start.date().strftime("%Y-%m-%d")
        response = client.get(f"/film-show/?start_date={query_date}")
        assert response.status_code == 200
        assert response.json() == [
            {
                "show_date": time["show_date"],
                "start_time": time["start_time"],
                "end_time": time["end_time"],
                "id_hall": id_hall,
                "id_film": id_film,
                "id": id_film_show,
            }
        ]


def test_filter_end_date():
    with TestClient(app) as client:
        # Current day + 5 days on 12:20
        first_show_start = datetime.datetime.combine(
            DEFAULT_TIME.date(), datetime.time(12, 20)
        )
        # Current day + 6 days on 12:20
        second_show_start = datetime.datetime.combine(
            DEFAULT_TIME.date() + datetime.timedelta(days=1), datetime.time(12, 20)
        )
        # Create first film show, return data to check the filter by end date
        (
            id_cinema,
            id_hall,
            id_film,
            id_film_show,
            time,
        ) = create_film_show_with_dependencies(
            client, show_dt=first_show_start, return_time=True
        )
        # Create second film show, no need to return any data
        create_film_show_with_dependencies(client, show_dt=second_show_start)
        # Check filter by end date, should return data of first film show
        query_date = first_show_start.date().strftime("%Y-%m-%d")
        response = client.get(f"/film-show/?end_date={query_date}")
        assert response.status_code == 200
        assert response.json() == [
            {
                "show_date": time["show_date"],
                "start_time": time["start_time"],
                "end_time": time["end_time"],
                "id_hall": id_hall,
                "id_film": id_film,
                "id": id_film_show,
            }
        ]


def test_filter_start_end_date():
    with TestClient(app) as client:
        # Current day + 5 days on 12:20
        first_show_start = datetime.datetime.combine(
            DEFAULT_TIME.date(), datetime.time(12, 20)
        )
        # Current day + 6 days on 12:20
        second_show_start = datetime.datetime.combine(
            DEFAULT_TIME.date() + datetime.timedelta(days=1), datetime.time(12, 20)
        )
        # Current day + 7 days on 12:20
        third_show_start = datetime.datetime.combine(
            DEFAULT_TIME.date() + datetime.timedelta(days=2), datetime.time(12, 20)
        )
        # Create first film show with first show time, no need to return any data
        create_film_show_with_dependencies(client, show_dt=first_show_start)
        # Create second film show with second show time, return data to check the filter response
        (
            id_cinema,
            id_hall,
            id_film,
            id_film_show,
            time,
        ) = create_film_show_with_dependencies(
            client, show_dt=second_show_start, return_time=True
        )
        # Create third film show with third show time, no need to return any data
        create_film_show_with_dependencies(client, show_dt=third_show_start)
        # Check start_date and end_date filter together, should return only data of second film show
        query_date = second_show_start.date().strftime("%Y-%m-%d")
        response = client.get(
            f"/film-show/?start_date={query_date}&end_date={query_date}"
        )
        assert response.status_code == 200
        assert response.json() == [
            {
                "show_date": time["show_date"],
                "start_time": time["start_time"],
                "end_time": time["end_time"],
                "id_hall": id_hall,
                "id_film": id_film,
                "id": id_film_show,
            }
        ]


def test_incorrect_date_format():
    with TestClient(app) as client:
        response = client.get(f"/film-show/?start_date=11111")
        assert response.status_code == 400
        response = client.get(f"/film-show/?end_date=11111")
        assert response.status_code == 400


def test_night_film_show():
    with TestClient(app) as client:
        # Current day + 5 days on 01:30 - night film show
        show_start = datetime.datetime.combine(
            DEFAULT_TIME.date(), datetime.time(1, 30)
        )
        # Create film show, return data to check logic for night show with using date filter
        (
            id_cinema,
            id_hall,
            id_film,
            id_film_show,
            time,
        ) = create_film_show_with_dependencies(
            client, show_dt=show_start, return_time=True
        )
        film_show_data = {
            "show_date": time["show_date"],
            "start_time": time["start_time"],
            "end_time": time["end_time"],
            "id_hall": id_hall,
            "id_film": id_film,
            "id": id_film_show,
        }
        # Check that film show (night show) is included in film show list of previous day of the date
        query_date = (DEFAULT_TIME.date() - datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        response = client.get(
            f"/film-show/?start_date={query_date}&end_date={query_date}"
        )
        assert response.status_code == 200
        assert response.json() == [film_show_data]
        # Check that film show (night show) is excluded in film show list of the date
        query_date = DEFAULT_TIME.date().strftime("%Y-%m-%d")
        response = client.get(
            f"/film-show/?start_date={query_date}&end_date={query_date}"
        )
        assert response.status_code == 200
        assert response.json() == []
