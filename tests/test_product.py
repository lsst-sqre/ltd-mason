from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *
from future.standard_library import install_aliases
install_aliases()

import tempfile
import shutil
import os

import pkg_resources
import pytest
import sh

from ltdmason.product import Product
from ltdmason.manifest import Manifest


@pytest.fixture
def demo_science_pipelines_manifest():
    resource_args = (__name__, 'demo_science_pipelines_manifest.yaml')
    assert pkg_resources.resource_exists(*resource_args)
    yaml_data = pkg_resources.resource_string(*resource_args)
    return yaml_data


def test_clone_doc_repo(demo_science_pipelines_manifest):
    manifest = Manifest(demo_science_pipelines_manifest)

    # future doesn't have this?
    # with tempfile.TemporaryDirectory() as build_dir:
    #     product = Product(manifest, build_dir)
    #     product.clone_doc_repo()
    #     assert os.path.exists(product.doc_dir)

    build_dir = tempfile.mkdtemp()
    
    product = Product(manifest, build_dir)
    product.clone_doc_repo()
    assert os.path.exists(product.doc_dir)
    # verify the correct ref is checked out
    git = sh.git.bake(_cwd=product.doc_dir)
    ref = str(git('symbolic-ref', 'HEAD').strip())
    print(ref)
    print(manifest.doc_repo_ref)
    assert ref.endswith(manifest.doc_repo_ref)

    shutil.rmtree(build_dir)
