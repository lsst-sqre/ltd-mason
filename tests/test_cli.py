"""Test the ltd-mason CLI features."""

from base64 import b64encode

import responses
import pytest

from ltdmason.cli import get_keeper_token


@responses.activate
def test_get_keeper_token():
    """Test getting a token from LTD Keeper."""
    expected_json = {'token': 'shake-it-off-shake-it-off'}
    responses.add(
        responses.GET,
        'http://localhost:5000/token',
        json=expected_json,
        status=200)

    _auth_header = 'Basic ' + b64encode(('user:pass')
                                        .encode('utf-8')).decode('utf-8')

    token = get_keeper_token('http://localhost:5000', 'user', 'pass')

    assert responses.calls[0].request.url == 'http://localhost:5000/token'
    assert responses.calls[0].request.headers['Authorization'] \
        == _auth_header
    assert token == 'shake-it-off-shake-it-off'


@responses.activate
def test_get_keeper_token_error():
    """Test with server error."""
    expected_json = {'token': 'shake-it-off-shake-it-off'}
    responses.add(
        responses.GET,
        'http://localhost:5000/token',
        json=expected_json,
        status=401)

    with pytest.raises(RuntimeError):
        get_keeper_token('http://localhost:5000', 'user', 'pass')
