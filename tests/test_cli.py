"""Test the ltd-mason CLI features."""

from base64 import b64encode

import responses
import pytest

from ltdmason.cli import get_keeper_token, read_keeper_credentials


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


def test_read_keeper_credentials(monkeypatch):
    """Basic test of read_keeper_credentials()"""
    _url = 'http://ltd-keeper.lsst.codes'
    _user = 'user'
    _pass = 'pass'
    monkeypatch.setenv('LTD_KEEPER_URL', _url)
    monkeypatch.setenv('LTD_KEEPER_USER', _user)
    monkeypatch.setenv('LTD_KEEPER_PASSWORD', _pass)

    c = read_keeper_credentials()
    assert c['keeper_url'] == _url
    assert c['keeper_username'] == _user
    assert c['keeper_password'] == _pass


@pytest.mark.parametrize('missing', ['LTD_KEEPER_URL', 'LTD_KEEPER_USER',
                                     'LTD_KEEPER_PASSWORD'])
def test_read_keeper_credentials_missing(monkeypatch, missing):
    """Test that read_keeper_credentials raises a RuntimeError when a necessary
    environment variable is missing.
    """
    _url = 'http://ltd-keeper.lsst.codes'
    _user = 'user'
    _pass = 'pass'
    monkeypatch.setenv('LTD_KEEPER_URL', _url)
    monkeypatch.setenv('LTD_KEEPER_USER', _user)
    monkeypatch.setenv('LTD_KEEPER_PASSWORD', _pass)

    monkeypatch.delenv(missing)

    with pytest.raises(RuntimeError):
        read_keeper_credentials()
