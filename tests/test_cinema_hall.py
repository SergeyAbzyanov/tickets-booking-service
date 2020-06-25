import pytest

from fastapi.testclient import TestClient
from src.main import app
from .create_functions import create_cinema, create_cinema_hall


def test_empty_list():
    with TestClient(app) as client:
        response = client.get("/cinema-hall/")
        assert response.status_code == 200
        assert response.json() == []


def test_create():
    with TestClient(app) as client:
        hall_data = {"name": "First", "rows": 20, "places_in_row": 20}
        # Create cinema
        id_cinema = create_cinema(client)
        # Check cinema hall create
        response = client.post(f"/cinema/{id_cinema}/hall/", json=hall_data)
        assert response.status_code == 200, response.json()
        hall_data["id"] = response.json()["id"]
        hall_data["id_cinema"] = id_cinema
        assert response.json() == hall_data


def test_create_cinema_id_not_found():
    with TestClient(app) as client:
        id_cinema = 99
        response, id_hall = create_cinema_hall(client, id_cinema)
        assert response.status_code == 404


def test_list():
    with TestClient(app) as client:
        # Create cinema
        id_cinema = create_cinema(client)
        # Create new cinema hall
        response, id_hall = create_cinema_hall(client, id_cinema)
        # Check new cinema hall in cinema hall list
        response = client.get("/cinema-hall/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": id_hall,
                "name": "First",
                "id_cinema": id_cinema,
                "rows": 20,
                "places_in_row": 20,
            }
        ]


def test_get():
    with TestClient(app) as client:
        # Create cinema
        id_cinema = create_cinema(client)
        # Create cinema hall
        response, id_hall = create_cinema_hall(client, id_cinema)
        # Check new cinema hall by id
        response = client.get(f"/cinema-hall/{id_hall}")
        assert response.status_code == 200
        assert response.json() == {
            "name": "First",
            "id_cinema": id_cinema,
            "id": id_hall,
            "rows": 20,
            "places_in_row": 20,
        }


def test_get_not_found():
    with TestClient(app) as client:
        # Check new cinema hall by id
        response = client.get(f"/cinema-hall/{99}")
        assert response.status_code == 404


@pytest.mark.parametrize(
    "key,value", [("name", "Great"), ("rows", 40), ("places_in_row", 40)]
)
def test_update(key, value):
    with TestClient(app) as client:
        # Create cinema
        id_cinema = create_cinema(client)
        # Create cinema hall
        response, id_hall = create_cinema_hall(client, id_cinema)
        # Update cinema hall
        response = client.patch(f"/cinema-hall/{id_hall}", json={key: value})
        assert response.status_code == 200
        # Check new cinema hall by id
        response = client.get(f"/cinema-hall/{id_hall}")
        assert response.status_code == 200
        expected = {
            "id": id_hall,
            "name": "First",
            "rows": 20,
            "places_in_row": 20,
            "id_cinema": id_cinema,
        }
        expected.update({key: value})
        assert response.json() == expected


def test_update_not_found():
    with TestClient(app) as client:
        response = client.patch(f"/cinema-hall/{99}", json={"name": "First"})
        assert response.status_code == 404
