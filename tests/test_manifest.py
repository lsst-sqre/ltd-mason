"""Test ltdmason.manifest."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()

import pkg_resources
import pytest

from ltdmason.manifest import Manifest


@pytest.fixture
def demo_science_pipelines_manifest():
    resource_args = (__name__, 'demo_science_pipelines_manifest.yaml')
    assert pkg_resources.resource_exists(*resource_args)
    yaml_data = pkg_resources.resource_string(*resource_args)
    return yaml_data


@pytest.mark.xfail
def test_manifest_roundtrip(demo_science_pipelines_manifest):
    # Can't get perfect round-trip equality of the YAML
    manifest = Manifest(demo_science_pipelines_manifest)
    assert manifest.yaml == demo_science_pipelines_manifest


def test_manifest_parse(demo_science_pipelines_manifest):
    manifest = Manifest(demo_science_pipelines_manifest)
    assert manifest.data['refs'][0] == 'master'
    assert 'url' in manifest.data['doc_repo']
    assert 'ref' in manifest.data['doc_repo']
    assert 'afw' in manifest.data['packages']
    assert 'dir' in manifest.data['packages']['afw']
    assert 'url' in manifest.data['packages']['afw']
    assert 'ref' in manifest.data['packages']['afw']
    assert manifest.data['product_name'] == 'lsst_apps'
    assert manifest.data['build_id'] == 'b1'
    assert manifest.data['requester_github_handle'] == 'jonathansick'
    assert manifest.data['doc_repo']['url'] == 'https://github.com/lsst-sqre/pipelines_docs.git'  # NOQA
    assert manifest.data['doc_repo']['ref'] == 'master'
    assert manifest.data['packages']['afw']['url'] == 'https://github.com/lsst/afw.git'  # NOQA
    assert manifest.data['packages']['afw']['ref'] == 'master'


def test_doc_repo_data(demo_science_pipelines_manifest):
    manifest = Manifest(demo_science_pipelines_manifest)
    assert 'pipelines_docs' == manifest.doc_repo_name
    assert 'master' == manifest.doc_repo_ref
    assert 'https://github.com/lsst-sqre/pipelines_docs.git' \
        == manifest.doc_repo_url
    assert 'lsst_apps' == manifest.product_name
    assert 'b1' == manifest.build_id
    assert 'jonathansick' == manifest.requester_github_handle
    assert ['master'] == manifest.refs
    assert 'https://github.com/lsst/afw.git' == manifest.packages['afw']['url']
    assert 'master' == manifest.packages['afw']['ref']
