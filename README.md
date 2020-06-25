# Getting Started

```shell script
$ uvicorn src.main:app --reload
```

# Docker - build and run

```shell script
$ docker-compose build
$ docker-compose run --service-ports tickets-booking app
```

# Docker - run tests

```shell script
$  docker-compose run tickets-booking pytest -vv
```

# Docker - stop/shutdown containers

```shell script
$ docker-compose down
```