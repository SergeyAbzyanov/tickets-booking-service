from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime, timedelta
from .create_functions import create_film_show_with_dependencies, create_booking


def test_empty_list():
    with TestClient(app) as client:
        response = client.get("/booking/")
        assert response.status_code == 200
        assert response.json() == []


def test_create():
    with TestClient(app) as client:
        # Full creation - cinema, hall, film, film show
        id_cinema, id_hall, id_film, id_film_show = create_film_show_with_dependencies(
            client
        )
        # Create booking
        booking_data = {"id_film_show": id_film_show, "row": 20, "place": 20}
        response = client.post("/booking/", json=booking_data)
        assert response.status_code == 200, response.json()
        booking_data["id"] = response.json()["id"]
        assert response.json() == booking_data


def test_list():
    with TestClient(app) as client:
        # Full creation - cinema, hall, film, film show
        id_cinema, id_hall, id_film, id_film_show = create_film_show_with_dependencies(
            client
        )
        # Create booking
        response, id_booking = create_booking(client, id_film_show)
        # Check booking list
        response = client.get("/booking/")
        assert response.status_code == 200
        assert response.json() == [
            {"id": id_booking, "id_film_show": id_film_show, "row": 20, "place": 20}
        ]


def test_get():
    with TestClient(app) as client:
        # Full creation - cinema, hall, film, film show
        id_cinema, id_hall, id_film, id_film_show = create_film_show_with_dependencies(
            client
        )
        # Create booking
        response, id_booking = create_booking(client, id_film_show)
        # Check booking
        response = client.get(f"/booking/{id_booking}")
        assert response.status_code == 200
        assert response.json() == {
            "id": id_booking,
            "id_film_show": id_film_show,
            "row": 20,
            "place": 20,
        }


def test_get_not_found():
    with TestClient(app) as client:
        response = client.get(f"/booking/{99}")
        assert response.status_code == 404


def test_create_occupied_place():
    with TestClient(app) as client:
        # Full creation - cinema, hall, film, film show
        id_cinema, id_hall, id_film, id_film_show = create_film_show_with_dependencies(
            client
        )
        # Check create occupied place
        create_booking(client, id_film_show)
        response, id_booking = create_booking(client, id_film_show)
        assert response.status_code == 400


def test_create_past_show_time():
    with TestClient(app) as client:
        # Full creation with past show time
        show_dt = datetime.now() - timedelta(days=2)
        id_cinema, id_hall, id_film, id_film_show = create_film_show_with_dependencies(
            client, show_dt=show_dt
        )
        # Create booking
        response, id_booking = create_booking(client, id_film_show)
        assert response.status_code == 400


def test_delete():
    with TestClient(app) as client:
        # Full creation - cinema, hall, film, film show
        id_cinema, id_hall, id_film, id_film_show = create_film_show_with_dependencies(
            client
        )
        # Create booking
        response, id_booking = create_booking(client, id_film_show)
        # Delete booking
        response = client.delete(f"/booking/{id_booking}")
        assert response.status_code == 200
        response = client.get(f"/booking/{id_booking}")
        assert response.status_code == 404


def test_delete_not_found():
    with TestClient(app) as client:
        response = client.delete(f"/booking/{99}")
        assert response.status_code == 404
