import pytest

from fastapi.testclient import TestClient
from src.main import app
from .create_functions import (
    create_cinema,
    create_cinema_hall,
    create_film_show_with_dependencies,
)


def test_empty_list():
    with TestClient(app) as client:
        response = client.get("/cinema/")
        assert response.status_code == 200
        assert response.json() == []


def test_create():
    with TestClient(app) as client:
        cinema_data = {"name": "Star", "city": "Moscow"}
        # Check cinema create
        response = client.post("/cinema/", json=cinema_data)
        assert response.status_code == 200, response.json()
        cinema_data["id"] = response.json()["id"]
        assert response.json() == cinema_data


def test_list():
    with TestClient(app) as client:
        # Create new cinema
        id_cinema = create_cinema(client)
        # Check new cinema in cinema list
        response = client.get("/cinema/")
        assert response.status_code == 200
        assert response.json() == [{"id": id_cinema, "name": "Star", "city": "Moscow"}]


def test_get():
    with TestClient(app) as client:
        # Create
        id_cinema = create_cinema(client)
        # Check new cinema by id
        response = client.get(f"/cinema/{id_cinema}")
        assert response.status_code == 200
        assert response.json() == {"id": id_cinema, "name": "Star", "city": "Moscow"}


def test_get_not_found():
    with TestClient(app) as client:
        # Check new cinema by id
        response = client.get(f"/cinema/{99}")
        assert response.status_code == 404


@pytest.mark.parametrize("key,value", [("name", "Superstar"), ("city", "Novosibirsk")])
def test_update(key, value):
    with TestClient(app) as client:
        # Create
        id_cinema = create_cinema(client)
        response = client.patch(f"/cinema/{id_cinema}", json={key: value})
        assert response.status_code == 200
        # Check new cinema by id
        response = client.get(f"/cinema/{id_cinema}")
        assert response.status_code == 200
        expected = {"id": id_cinema, "name": "Star", "city": "Moscow"}
        expected.update({key: value})
        assert response.json() == expected


def test_update_not_found():
    with TestClient(app) as client:
        response = client.patch(
            f"/cinema/{99}", json={"name": "Star", "city": "Moscow"}
        )
        assert response.status_code == 404


def test_hall_list():
    with TestClient(app) as client:
        # Create cinema
        id_cinema = create_cinema(client)
        # Create new cinema hall
        response, id_hall = create_cinema_hall(client, id_cinema)
        # Check new cinema hall in cinema hall list
        response = client.get(f"/cinema/{id_cinema}/hall/")
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


def test_hall_get():
    with TestClient(app) as client:
        # Create cinema
        id_cinema = create_cinema(client)
        # Create new cinema hall
        response, id_hall = create_cinema_hall(client, id_cinema)
        # Check new cinema hall in cinema hall list
        response = client.get(f"/cinema/{id_cinema}/hall/{id_hall}")
        assert response.status_code == 200
        assert response.json() == {
            "id": id_hall,
            "name": "First",
            "id_cinema": id_cinema,
            "rows": 20,
            "places_in_row": 20,
        }


def test_hall_get_not_found():
    with TestClient(app) as client:
        # Create cinema
        id_cinema = create_cinema(client)
        # Use fake id hall
        id_hall = 99
        response = client.get(f"/cinema/{id_cinema}/hall/{id_hall}")
        assert response.status_code == 404


def test_film_show_list():
    with TestClient(app) as client:
        (
            id_cinema,
            id_hall,
            id_film,
            id_film_show,
            time,
        ) = create_film_show_with_dependencies(client, return_time=True)
        # Check film show list by cinema and hall
        response = client.get(f"/cinema/{id_cinema}/hall/{id_hall}/film-show/")
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


def test_film_show_list_404():
    with TestClient(app) as client:
        # Use fake id cinema and id hall
        id_cinema = 99
        id_hall = 99
        response = client.get(f"/cinema/{id_cinema}/hall/{id_hall}/film-show/")
        assert response.status_code == 404
        # Use real id cinema and fake id hall
        id_cinema = create_cinema(client)
        response = client.get(f"/cinema/{id_cinema}/hall/{id_hall}/film-show/")
        assert response.status_code == 404
        # Use real id cinema and id hall but film shows not found
        response, id_hall = create_cinema_hall(client, id_cinema)
        response = client.get(f"/cinema/{id_cinema}/hall/{id_hall}/film-show/")
        assert response.status_code == 404
