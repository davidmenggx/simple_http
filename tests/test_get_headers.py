import pytest

from utilities import get_headers

def test_valid_headers():
    assert get_headers(['Header1: Value1', 'Header2: Value2']) == {'header1': 'value1', 'header2': 'value2'}
    assert get_headers([]) == {}

def test_invalid_headers():
    with pytest.raises(ValueError):
        get_headers(['Header1: This header is: too long'])
    with pytest.raises(ValueError):
        get_headers(['Header1 has no colon'])
    with pytest.raises(ValueError):
        get_headers([''])