from utilities import get_etag

def test_index_etag():
    assert get_etag('public/index.html') == 'd628372f0858fd371264b93099ffb9b741292ae4a5b06fa3d31ddd2c31d6b38d'

def test_invalid_etags():
    assert get_etag('invalid') == ''
    assert get_etag('public/invalid.html') == ''
    assert get_etag('') == ''