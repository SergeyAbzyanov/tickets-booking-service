import datetime


def create_cinema(client):
    response = client.post("/cinema/", json={"name": "Star", "city": "Moscow"})
    assert response.status_code == 200, response.json()
    id_cinema = response.json()["id"]
    return id_cinema


def create_cinema_hall(client, id_cinema):
    response = client.post(
        f"/cinema/{id_cinema}/hall/",
        json={"name": "First", "rows": 20, "places_in_row": 20},
    )
    if response.status_code != 200:
        return response, ""
    assert response.status_code == 200, response.json()
    id_hall = response.json()["id"]
    return response, id_hall


def create_film(client, return_duration=False):
    response = client.post(
        "/film/",
        json={
            "title": "The Avengers",
            "genre": "Fantastic",
            "cast": "Robert Downey Jr., Chris Evans, Chris Hemsworth, Tom Hiddleston",
            "description": "Big fight",
            "duration": 120,
        },
    )
    assert response.status_code == 200, response.json()
    id_film = response.json()["id"]
    if return_duration:
        return response, id_film, 120
    return response, id_film


def create_film_show(client, id_hall, id_film, show_dt):
    response = client.post(
        "/film-show/",
        json={
            "start_time": show_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "id_hall": id_hall,
            "id_film": id_film,
        },
    )
    if response.status_code != 200:
        return response, ""
    assert response.status_code == 200, response.json()
    id_film_show = response.json()["id"]
    return response, id_film_show


def create_booking(client, id_film_show, row=20, place=20):
    response = client.post(
        "/booking/", json={"id_film_show": id_film_show, "row": row, "place": place}
    )
    if response.status_code != 200:
        return response, ""
    assert response.status_code == 200, response.json()
    id_booking = response.json()["id"]
    return response, id_booking


def create_film_show_dependencies(client, return_duration=False):
    # Create cinema
    id_cinema = create_cinema(client)
    # Create cinema hall
    response, id_hall = create_cinema_hall(client, id_cinema)
    if return_duration:
        response, id_film, film_duration = create_film(client, return_duration=True)
        return id_hall, id_film, film_duration
    else:
        response, id_film = create_film(client)
        return id_hall, id_film


def create_film_show_with_dependencies(
    client,
    show_dt=datetime.datetime.now() + datetime.timedelta(days=2),
    return_time=False,
):
    # Create cinema
    id_cinema = create_cinema(client)
    # Create cinema hall
    response, id_hall = create_cinema_hall(client, id_cinema)
    # Create film and film show
    if return_time:
        response, id_film, duration = create_film(client, return_duration=True)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        time = preprocess_show_time(show_dt, duration)
        return id_cinema, id_hall, id_film, id_film_show, time
    else:
        response, id_film = create_film(client)
        response, id_film_show = create_film_show(client, id_hall, id_film, show_dt)
        return id_cinema, id_hall, id_film, id_film_show


def preprocess_show_time(show_dt, duration):
    time = {
        "show_date": str(show_dt.date()),
        "start_time": str(show_dt.time()),
        "end_time": str((show_dt + datetime.timedelta(minutes=duration)).time()),
    }
    return time
