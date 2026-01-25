import pytest
import random
from datetime import datetime, timezone

from handlers import get

@pytest.fixture
def seeded_random():
    random.seed(42)

def test_get_index(seeded_random, mocker):

    mock_etag = mocker.patch('handlers.get.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = get('/index.html', {}) 

    assert b'200 OK' in response
    assert b'mock_etag' in response

def test_get_root(seeded_random, mocker):
    mock_etag = mocker.patch('handlers.get.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = get('/', {}) 

    assert b'200 OK' in response
    assert b'mock_etag' in response

def test_path_traversal(mocker):
    mock_datetime = mocker.patch('constants.responses.datetime')
    mock_datetime.now.return_value = datetime(2026, 1, 25, 12, 0, 0, tzinfo=timezone.utc)

    response = get('../', {})

    assert b'403 Forbidden' in response

def test_invalid_path(mocker):
    response = get('/invalid.html', {})

    assert b'404 Not Found' in response

def test_cache_hit(seeded_random, mocker):
    mock_etag = mocker.patch('handlers.get.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = get('/', {'if-none-match': 'mock_etag'})

    assert b'304 Not Modified' in response