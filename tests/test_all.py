# tests/test_all.py
import pytest
from unittest.mock import Mock, patch
from unittest.mock import MagicMock
import sys
import os
ruta_superior = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ruta_superior)
config = { "urls": { "user_api": "https://api.generadordni.es/person/username?results=100", "pass_api": "https://api.generadordni.es/person/password?results=100", "domain_default": "https://localhost/", "google_check": "https://www.google.com" }, "proxy_sources": [ "https://www.proxy-list.download/api/v1/get?type=http", "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all" ], "target_domains": { "service_name": "example.com" }, "database": { "DATABASE_PATH": "data.db", "tables": { "proxys": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "ip TEXT", "port INT"], "Usernames": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "username TEXT"], "Passwords": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "password TEXT"], "Emails": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "email TEXT"], "Pastebins": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "url TEXT", "code TEXT"], "Combos": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "username TEXT", "password TEXT"], "Config": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "config_data TEXT"], "TargetSites": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "site_name TEXT", "domain_url TEXT"] } } }


from main import (
    create_tables,
    check_proxy,
    insert_proxy,
    insert_usernames,
    insert_passwords,
    get_usernames,
    get_passwords,
    generate_combos,
    request_web_combos
)

@pytest.fixture
def mock_config():
    return {"database": {"tables": {"table1": ["col1", "col2"]}}}

@pytest.fixture
def mock_sqlite_connect():
    return MagicMock()

def test_create_tables(mock_sqlite_connect, mock_config):
    with patch('main.sqlite3.connect', return_value=mock_sqlite_connect), \
         patch('main.config', return_value=mock_config):

        create_tables(mock_sqlite_connect, mock_config)

        mock_sqlite_connect.cursor.return_value.execute.assert_called_once_with("CREATE TABLE IF NOT EXISTS table1 (col1, col2)")

def test_check_proxy():
    with patch('main.requests.get') as mock_requests_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        proxy_result = check_proxy("mock_proxy")

        assert proxy_result == "mock_proxy"

def test_insert_proxy(mock_sqlite_connect):
    insert_proxy(mock_sqlite_connect, "mock_proxy")

    mock_sqlite_connect.cursor.return_value.execute.assert_called_once_with("INSERT INTO proxys (ip, port) VALUES (?, ?)", ("mock", "proxy"))

# Agrega tests similares para las demás funciones
