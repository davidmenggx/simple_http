import pytest
from unittest.mock import patch

from handlers import post

def test_post_appends_and_resets(tmp_path):
    fake_base = tmp_path / 'public'
    fake_api = fake_base / 'api'
    fake_api.mkdir(parents=True)

    test_file = fake_api / 'data.txt'
    test_file.write_text('initial content')

    with patch('handlers.post.BASE_DIR', fake_base), \
            patch('handlers.post.API_DIR', fake_api):
        
        payload = b' - new data'
        response = post('/api/data.txt', {}, body=payload)

        assert b'200 OK' in response
        assert test_file.read_text() == 'initial content - new data'

def test_post_file_not_found(tmp_path):
    fake_base = tmp_path / 'public'
    fake_api = fake_base / 'api'
    fake_api.mkdir(parents=True)

    with patch('handlers.post.BASE_DIR', fake_base), \
        patch('handlers.post.API_DIR', fake_api):
        
        response = post('/api/missing.txt', {}, body=b'data')
        
        assert b'404 Not Found' in response

def test_post_file_forbidden():
    response = post('../', {}, body=b'data')
        
    assert b'403 Forbidden' in response

@pytest.mark.parametrize('path', [
    '/', '/index.html', '/script.js', '/styles.css', 
    '/data/users.json', '/data/videos.json', '/images/img1.jpg'
])
def test_post_file_not_allowed(path):
    response = post(path, {})

    assert b'405 Method Not Allowed' in response
