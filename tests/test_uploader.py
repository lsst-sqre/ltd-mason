"""Tests for the ltdmason/uploader module."""

import responses
import pkg_resources
import pytest

from ltdmason.manifest import Manifest
from ltdmason.uploader import _register_build, _confirm_upload, KeeperError


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
