import pytest

from fastapi.testclient import TestClient
from src.main import app
from .create_functions import create_film


def test_empty_list():
    with TestClient(app) as client:
        response = client.get("/film/")
        assert response.status_code == 200
        assert response.json() == []


def test_create():
    with TestClient(app) as client:
        film_data = {
            "title": "The Avengers",
            "genre": "Fantastic",
            "cast": "Robert Downey Jr., Chris Evans, Chris Hemsworth, Tom Hiddleston",
            "description": "Big fight",
            "duration": 120,
        }
        # Check film create
        response = client.post("/film/", json=film_data)
        assert response.status_code == 200, response.json()
        film_data["id"] = response.json()["id"]
        assert response.json() == film_data


def test_list():
    with TestClient(app) as client:
        # Create new film
        response, id_film = create_film(client)
        # Check new film in film list
        response = client.get("/film/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "title": "The Avengers",
                "genre": "Fantastic",
                "cast": "Robert Downey Jr., Chris Evans, Chris Hemsworth, Tom Hiddleston",
                "description": "Big fight",
                "duration": 120,
                "id": id_film,
            }
        ]


def test_get():
    with TestClient(app) as client:
        # Create new film
        response, id_film = create_film(client)
        # Check new film by id
        response = client.get(f"/film/{id_film}")
        assert response.status_code == 200
        assert response.json() == {
            "title": "The Avengers",
            "genre": "Fantastic",
            "cast": "Robert Downey Jr., Chris Evans, Chris Hemsworth, Tom Hiddleston",
            "description": "Big fight",
            "duration": 120,
            "id": id_film,
        }


def test_get_not_found():
    with TestClient(app) as client:
        # Check new film by id
        response = client.get(f"/film/{99}")
        assert response.status_code == 404


@pytest.mark.parametrize(
    "key,value",
    [
        ("title", "Star Trek"),
        ("genre", "Fantasy"),
        ("cast", "Vin Diesel"),
        ("description", "Small fight"),
        ("duration", 140),
    ],
)
def test_update(key, value):
    with TestClient(app) as client:
        # Create new film
        response, id_film = create_film(client)
        # Update film
        response = client.patch(f"/film/{id_film}", json={key: value})
        assert response.status_code == 200
        # Check new film by id
        response = client.get(f"/film/{id_film}")
        assert response.status_code == 200
        expected = {
            "id": id_film,
            "title": "The Avengers",
            "genre": "Fantastic",
            "cast": "Robert Downey Jr., Chris Evans, Chris Hemsworth, Tom Hiddleston",
            "description": "Big fight",
            "duration": 120,
        }
        expected.update({key: value})
        assert response.json() == expected


def test_update_not_found():
    with TestClient(app) as client:
        response = client.patch(
            f"/film/{99}",
            json={
                "title": "The Avengers",
                "genre": "Fantastic",
                "cast": "Robert Downey Jr., Chris Evans, Chris Hemsworth, Tom Hiddleston",
                "description": "Big fight",
                "duration": 120,
            },
        )
        assert response.status_code == 404
