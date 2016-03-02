from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
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


@pytest.mark.skipif(os.getenv('STACK_AFW') is None,
                    reason='Requires $STACK_AFW to be set')
def test_link_package_repos(demo_science_pipelines_manifest):
    manifest = Manifest(demo_science_pipelines_manifest)

    build_dir = tempfile.mkdtemp()

    product = Product(manifest, build_dir)
    product.clone_doc_repo()
    product.link_package_repos()

    print(sh.ls('-al', product.doc_dir))

    for package_name, package_data in product.manifest.packages.items():
        print(package_name)
        # test that the package's directory exists in docs
        package_dir = os.path.join(build_dir, product.manifest.doc_repo_name,
                                   str(package_name))
        print(package_dir)
        assert os.path.isdir(package_dir)

        # test that the packages doc/_static directory is linked
        package_static_dir = os.path.join(package_data['dirname'],
                                          'doc', '_static', package_name)
        if os.path.exists(package_static_dir):
            doc_package_static_dir = os.path.join(product.doc_dir,
                                                  '_static', str(package_name))
            assert os.path.islink(doc_package_static_dir)
            assert os.path.isdir(doc_package_static_dir)

        # test that individual entities of a package's doc (aside from _static)
        # are linked
        source_dir = os.path.join(package_data['dirname'], 'doc')
        print('source_dir', source_dir)
        print(os.listdir(source_dir))
        target_dir = os.path.join(product.doc_dir, str(package_name))
        for entity in os.listdir(source_dir):
            print('entity', entity)
            if entity == '_static':
                continue
            link_name = os.path.join(target_dir, entity)
            assert os.path.islink(link_name)
            assert os.path.lexists(link_name)

    shutil.rmtree(build_dir)


@pytest.mark.skipif(os.getenv('STACK_AFW') is None,
                    reason='Requires $STACK_AFW to be set')
def test_sphinx_build(demo_science_pipelines_manifest):
    manifest = Manifest(demo_science_pipelines_manifest)

    build_dir = tempfile.mkdtemp()

    product = Product(manifest, build_dir)
    product.clone_doc_repo()
    product.link_package_repos()
    product.build_sphinx()

    assert os.path.exists(os.path.join(product.doc_dir, '_build', 'html'))

    shutil.rmtree(build_dir)
