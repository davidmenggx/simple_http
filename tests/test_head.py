import pytest
import random

from handlers import head

@pytest.fixture
def seeded_random():
    random.seed(42)

def test_head_index(seeded_random, mocker):
    mock_etag = mocker.patch('handlers.head.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = head('/index.html', {})

    assert b'200 OK' in response
    assert b'mock_etag' in response

def test_head_root(seeded_random, mocker):
    mock_etag = mocker.patch('handlers.head.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = head('/', {})

    assert b'200 OK' in response
    assert b'mock_etag' in response

def test_path_traversal(mocker):
    response = head('../', {}) 
    
    assert b'403 Forbidden' in response

def test_invalid_path(mocker):
    response = head('/invalid.html', {})

    assert b'404 Not Found' in response

def test_cache_hit(seeded_random, mocker):
    mock_etag = mocker.patch('handlers.head.get_etag')
    mock_etag.return_value = 'mock_etag'

    response = head('/', {'if-none-match': 'mock_etag'})

    assert b'304 Not Modified' in response