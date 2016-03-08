"""Test the ltd-mason CLI features."""

import os
from base64 import b64encode

import responses
import pytest

from ltdmason.cli import (get_keeper_token, read_keeper_credentials,
                          read_aws_credentials)


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


def test_read_aws_credentials_envvar(monkeypatch):
    """Test read_aws_credentials() if through environment variables."""
    v = {'LTD_MASON_AWS_ID': 'key-id',
         'LTD_MASON_AWS_SECRET': 'key-secret',
         'LTD_MASON_AWS_PROFILE': 'aws-profile'}
    missing = ('LTD_MASON_AWS_PROFILE',)

    def patch_envar(x):
        if x in missing:
            return None
        else:
            return v[x]

    monkeypatch.setattr(os, 'getenv', patch_envar)

    c = read_aws_credentials()
    print(c)
    assert c['aws_access_key_id'] == v['LTD_MASON_AWS_ID']
    assert c['aws_secret_access_key'] == v['LTD_MASON_AWS_SECRET']
    assert 'aws_profile' not in c


def test_read_aws_credentials_profile(monkeypatch):
    """Test read_aws_credentials() if through a profile environment variable.
    """
    v = {'LTD_MASON_AWS_ID': 'key-id',
         'LTD_MASON_AWS_SECRET': 'key-secret',
         'LTD_MASON_AWS_PROFILE': 'aws-profile'}
    missing = ('LTD_MASON_AWS_ID', 'LTD_MASON_AWS_SECRET')

    def patch_envar(x):
        if x in missing:
            return None
        else:
            return v[x]

    monkeypatch.setattr(os, 'getenv', patch_envar)

    c = read_aws_credentials()
    print(c)
    assert c['aws_profile'] == v['LTD_MASON_AWS_PROFILE']
    assert 'aws_access_key_id' not in c
    assert 'aws_secret_access_key' not in c


@pytest.mark.parametrize('missing', [('LTD_MASON_AWS_ID',
                                      'LTD_MASON_AWS_SECRET',
                                      'LTD_MASON_AWS_PROFILE'),
                                     ('LTD_MASON_AWS_ID',
                                      'LTD_MASON_AWS_PROFILE'),
                                     ('LTD_MASON_AWS_SECRET',
                                      'LTD_MASON_AWS_PROFILE')])
def test_read_aws_credentials_fallback(monkeypatch, missing):
    """Test read_aws_credentials() if environment variables are missing,
    which causes a fallback to assume the user has default configs for boto3.
    """
    v = {'LTD_MASON_AWS_ID': 'key-id',
         'LTD_MASON_AWS_SECRET': 'key-secret',
         'LTD_MASON_AWS_PROFILE': 'aws-profile'}

    def patch_envar(x):
        if x in missing:
            return None
        else:
            return v[x]

    monkeypatch.setattr(os, 'getenv', patch_envar)

    c = read_aws_credentials()
    print(c)
    assert len(c) == 0
