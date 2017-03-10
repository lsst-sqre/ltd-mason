"""Tests for the ltdmason/uploader module."""

import os
from base64 import b64encode
try:
    from unittest import mock
except ImportError:
    import mock
import responses
import pkg_resources
import pytest

from ltdmason.manifest import Manifest
from ltdmason.uploader import (_register_build, _confirm_upload, KeeperError,
                               upload_via_keeper, get_keeper_token,
                               read_keeper_credentials,
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
    """Test read_aws_credentials() if through environment variables.

    read_aws_credentials() is challenging to test because we not only test the
    presence of an environment variable, but also the absence. The delvar
    monkeypatch method only removes the monkeypatched var; an actual
    environment variable of the same name can still leak through. Instead we
    put the logic of omitting variables into a function that replaces
    os.getenv.
    """
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


@pytest.fixture
def demo_manifest():
    resource_args = (__name__, 'demo_manifest.yaml')
    assert pkg_resources.resource_exists(*resource_args)
    yaml_data = pkg_resources.resource_string(*resource_args)
    manifest = Manifest(yaml_data)
    return manifest


@responses.activate
def test_register_build_ok(demo_manifest):
    """Test that _register_build returns the correct values."""
    expected_json = {
        "bucket_name": "an-s3-bucket",
        "bucket_root_dir": "lsst_apps/builds/b1",
        "date_created": "2016-03-01T10:21:27.583795Z",
        "date_ended": None,
        "git_refs": ["master"],
        "github_requester": "jonathansick",
        "product_url": "http://localhost:5000/products/lsst_apps",
        "self_url": "http://localhost:5000/builds/1",
        "slug": "b1",
        "surrogate_key": "35d7a50a1d1b40ab9e7a56cd169f356e",
        "uploaded": False}
    responses.add(
        responses.POST,
        'http://localhost:5000/products/lsst_apps/builds/',
        json=expected_json,
        status=201)

    build_info = _register_build(demo_manifest,
                                 'http://localhost:5000',
                                 'token')
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url \
        == 'http://localhost:5000/products/lsst_apps/builds/'
    for k, v in expected_json.items():
        assert build_info[k] == v


@responses.activate
def test_register_build_failed(demo_manifest):
    """Test that KeeperError is raised for a bad response."""
    expected_json = {
        "bucket_name": "an-s3-bucket",
        "bucket_root_dir": "lsst_apps/builds/b1",
        "date_created": "2016-03-01T10:21:27.583795Z",
        "date_ended": None,
        "git_refs": ["master"],
        "github_requester": "jonathansick",
        "product_url": "http://localhost:5000/products/lsst_apps",
        "self_url": "http://localhost:5000/builds/1",
        "slug": "b1",
        "uploaded": False}
    responses.add(
        responses.POST,
        'http://localhost:5000/products/lsst_apps/builds/',
        json=expected_json,
        status=404)

    with pytest.raises(KeeperError):
        _register_build(demo_manifest,
                        'http://localhost:5000',
                        'token')
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url \
        == 'http://localhost:5000/products/lsst_apps/builds/'


@responses.activate
def test_confirm_upload_ok():
    url = 'http://localhost:5000/builds/1'

    responses.add(
        responses.PATCH,
        url,
        json={'uploaded': True},
        status=200)

    _confirm_upload('http://localhost:5000/builds/1', 'token')
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
def test_confirm_upload_failed():
    """Check that an exception is raised when keeper does not return 200
    on an upload confirmation reques.
    """
    url = 'http://localhost:5000/builds/1'

    responses.add(
        responses.PATCH,
        url,
        json={'uploaded': True},
        status=404)

    with pytest.raises(KeeperError):
        _confirm_upload('http://localhost:5000/builds/1', 'token')
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


def test_upload_via_keeper(demo_manifest, mocker):
    """Test upload_via_keeper.

    The goal is to ensure that it

    1. registers a build
    2. Calls upload with the right attributes
    3. Confirms the upload
    """
    build_resource = {
        "bucket_name": "an-s3-bucket",
        "bucket_root_dir": "lsst_apps/builds/b1",
        "date_created": "2016-03-01T10:21:27.583795Z",
        "date_ended": None,
        "git_refs": ["master"],
        "github_requester": "jonathansick",
        "product_url": "http://localhost:5000/products/lsst_apps",
        "self_url": "http://localhost:5000/builds/1",
        "slug": "b1",
        "surrogate_key": "35d7a50a1d1b40ab9e7a56cd169f356e",
        "uploaded": False}
    mock_register = mocker.patch('ltdmason.uploader._register_build')
    mock_register.return_value = build_resource
    mock_upload = mocker.patch('ltdmason.uploader.s3upload_upload')
    mock_confirm = mocker.patch('ltdmason.uploader._confirm_upload')

    mock_product = mock.MagicMock()
    mock_product.html_dir = '_build/html'

    upload_via_keeper(demo_manifest, mock_product,
                      'https://ltd-keeper.example.org', 'token')

    # Check that upload_via_keeper called the right things
    assert mock_register.call_count == 1
    assert mock_upload.call_count == 1
    assert mock_confirm.call_count == 1

    mock_register.assert_called_once_with(
        demo_manifest, 'https://ltd-keeper.example.org', 'token')

    mock_upload.assert_called_once_with(
        build_resource['bucket_name'],
        build_resource['bucket_root_dir'],
        mock_product.html_dir,
        surrogate_key=build_resource['surrogate_key'],
        acl=None,
        cache_control_max_age=31536000)

    mock_confirm.assert_called_once_with(build_resource['self_url'], 'token')
