FROM python:3.8.2-slim

COPY ./requirements.txt /app/
WORKDIR /app/

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["help"]