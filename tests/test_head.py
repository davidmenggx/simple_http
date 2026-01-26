import pytest
import random
from unittest.mock import ANY

from handlers import head

@pytest.fixture
def seeded_random():
    random.seed(42)

def test_head_index(mocker):
    mock_etag = mocker.patch('handlers.head.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = head('/index.html', {})

    assert b'200 OK' in response
    assert b'mock_etag' in response

def test_head_root(mocker):
    mock_etag = mocker.patch('handlers.head.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = head('/', {})

    assert b'200 OK' in response
    assert b'mock_etag' in response

def test_path_traversal():
    response = head('../', {}) 
    
    assert b'403 Forbidden' in response

def test_invalid_path():
    response = head('/invalid.html', {})

    assert b'404 Not Found' in response

def test_cache_hit(mocker):
    mock_etag = mocker.patch('handlers.head.get_etag')
    mock_etag.return_value = 'mock_etag'

    response1 = head('/', {'if-none-match': 'mock_etag'})
    response2 = head('/', {'if-none-match': '"mock_etag"'})

    assert b'304 Not Modified' in response1
    assert b'304 Not Modified' in response2

def test_keepalive_connection():
    response1 = head('/', {'connection': 'close'})
    response2 = head('/', {})

    assert b'Connection: Close' in response1
    assert b'Connection: Keep-Alive' in response2

def test_file_not_found_during_read(mocker):
    mock_file = mocker.patch('builtins.open')
    mock_file.side_effect = FileNotFoundError("File removed")

    response = head('/', {})

    assert b'404 Not Found' in response
    mock_file.assert_called_once_with(ANY, 'rb')

def test_internal_server_error(mocker):
    mocker.patch('handlers.head.get_etag', side_effect=RuntimeError("Unexpected failure"))

    response = head('/', {})

    assert b'500 Internal Server Error' in response