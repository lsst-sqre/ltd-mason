"""Tests for the ltdmason/uploader module."""

try:
    from unittest import mock
except ImportError:
    import mock
import responses
import pkg_resources
import pytest

from ltdmason.manifest import Manifest
from ltdmason.uploader import (_register_build, _confirm_upload, KeeperError,
                               upload_via_keeper)


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
    mock_upload = mocker.patch('ltdmason.uploader.upload')
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
        acl='public-read',
        cache_control_max_age=31536000)

    mock_confirm.assert_called_once_with(build_resource['self_url'], 'token')
