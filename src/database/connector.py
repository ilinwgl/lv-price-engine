import os

import psycopg
from dotenv import load_dotenv
from psycopg import Connection

load_dotenv()


class DBConnector:
    def __init__(self) -> None:
        self._host = os.getenv("DB_HOST")
        self._port = os.getenv("DB_PORT")
        self._name = os.getenv("DB_NAME")
        self._user = os.getenv("DB_USER")
        self._password = os.getenv("DB_PASSWORD")

    def connect(self) -> Connection:
        return psycopg.connect(
            host=self._host,
            port=self._port,
            dbname=self._name,
            user=self._user,
            password=self._password,
        )
