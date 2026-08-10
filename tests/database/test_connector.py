from unittest.mock import patch

from src.database.connector import DBConnector


@patch("src.database.connector.psycopg.connect")
def test_connect(mock_connect, monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "kalkulation_db")
    monkeypatch.setenv("DB_USER", "kalkulation_user")
    monkeypatch.setenv("DB_PASSWORD", "password")

    connector = DBConnector()

    connector.connect()

    mock_connect.assert_called_once_with(
        host="localhost",
        port="5432",
        dbname="kalkulation_db",
        user="kalkulation_user",
        password="password",
    )
