import os

DB_USER = os.getenv("DB_USER", "cinema")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cinema")
DB_NAME = os.getenv("DB_NAME", "tickets")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
