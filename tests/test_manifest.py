"""Test ltdmason.manifest."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import pkg_resources
import pytest
from jsonschema import ValidationError
import ruamel.yaml

from ltdmason.manifest import Manifest, TravisManifest


@pytest.fixture
def demo_manifest():
    resource_args = (__name__, 'demo_manifest.yaml')
    assert pkg_resources.resource_exists(*resource_args)
    yaml_data = pkg_resources.resource_string(*resource_args)
    return yaml_data


@pytest.mark.xfail
def test_manifest_roundtrip(demo_manifest):
    # Can't get perfect round-trip equality of the YAML
    manifest = Manifest(demo_manifest)
    assert manifest.yaml == demo_manifest


def test_doc_repo_data(demo_manifest):
    manifest = Manifest(demo_manifest)
    assert 'pipelines_docs' == manifest.doc_repo_name
    assert 'master' == manifest.doc_repo_ref
    assert 'https://github.com/lsst-sqre/pipelines_docs.git' \
        == manifest.doc_repo_url
    assert 'lsst_apps' == manifest.product_name
    assert 'b1' == manifest.build_id
    assert 'jonathansick' == manifest.requester_github_handle
    assert ['master'] == manifest.refs
    assert 'https://github.com/lsst/afw.git' == manifest.packages['afw']['url']
    assert '/mnt/stack_docs/lsstsw/stack/Linux64/afw/2015_10.0-14-g7c5ed66' \
        == manifest.packages['afw']['dir']
    assert 'master' == manifest.packages['afw']['ref']


@pytest.mark.parametrize('key', ['product_name', 'build_id', 'refs',
                                 'requester_github_handle', 'doc_repo',
                                 'packages'])
def test_missing_manifest_fields(demo_manifest, key):
    """Test that exceptions are raised when a manifest is missing required
    fields.
    """
    manifest = ruamel.yaml.load(demo_manifest)
    del manifest[key]
    with pytest.raises(ValidationError):
        Manifest.validate(manifest)


@pytest.mark.parametrize('key', ['url', 'ref'])
def test_missing_manifest_doc_repo_fields(demo_manifest, key):
    """Test that exceptions are raised when a manifest is missing required
    fields in the 'doc_repo' object
    """
    manifest = ruamel.yaml.load(demo_manifest)
    del manifest['doc_repo'][key]
    with pytest.raises(ValidationError):
        Manifest.validate(manifest)


@pytest.mark.parametrize('key', ['dir', 'url', 'ref'])
def test_missing_manifest_package_fields(demo_manifest, key):
    """Test that exceptions are raised when a manifest is missing required
    fields in the 'packages.packages.afw' object.
    """
    manifest = ruamel.yaml.load(demo_manifest)
    del manifest['packages']['afw'][key]
    with pytest.raises(ValidationError):
        Manifest.validate(manifest)


def test_bad_refs_type(demo_manifest):
    """Test that refs is a list."""
    manifest = ruamel.yaml.load(demo_manifest)
    manifest['refs'] = 'master'
    with pytest.raises(ValidationError):
        Manifest.validate(manifest)


def test_travis_manifest(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'master')
    monkeypatch.setenv('TRAVIS_REPO_SLUG', 'lsst-sqre/ltd-keeper')
    monkeypatch.setenv('LTD_MASON_PRODUCT', 'ltd-keeper')

    manifest = TravisManifest()
    assert manifest.doc_repo_url \
        == 'https://github.com/lsst-sqre/ltd-keeper.git'
    assert manifest.doc_repo_ref == 'master'
    assert manifest.product_name == 'ltd-keeper'
    assert manifest.build_id is None
    assert manifest.requester_github_handle is None
    assert manifest.refs == ['master']
    assert len(manifest.packages) == 0


def test_travis_manifest_missing_envvars(monkeypatch):
    monkeypatch.delenv('TRAVIS_BRANCH', raising=False)
    monkeypatch.delenv('TRAVIS_REPO_SLUG', raising=False)
    monkeypatch.delenv('LTD_MASON_PRODUCT', raising=False)

    manifest = TravisManifest()

    with pytest.raises(RuntimeError):
        manifest.doc_repo_url
    with pytest.raises(RuntimeError):
        manifest.doc_repo_ref
    with pytest.raises(RuntimeError):
        manifest.product_name
    with pytest.raises(RuntimeError):
        manifest.refs
