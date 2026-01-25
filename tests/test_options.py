import pytest

from handlers import options

@pytest.mark.parametrize('path', [
    '/', '/index.html', '/script.js', '/styles.css', 
    '/data/users.json', '/data/videos.json', '/images/img1.jpg'
])
def test_options_static_files(path):
    response = options(path, {})
    assert b'204 No Content' in response
    assert b'Allow: OPTIONS, GET, HEAD' in response

@pytest.mark.parametrize('path', [
    '/api/comments.json', '/api/public_file.txt'
])
def test_options_api_files(path):
    response = options(path, {})

    assert b'204 No Content' in response
    assert b'Allow: OPTIONS, GET, HEAD, POST' in response

def test_path_traversal():
    response = options('../', {})

    assert b'403 Forbidden' in response

def test_invalid_path():
    response = options('/invalid.html', {})
    
    assert b'404 Not Found' in response
