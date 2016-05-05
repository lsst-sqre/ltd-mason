"""Test the Product build process using a mock documentation.

See mock_manifest.yaml; the doc repo is github.com/lsst-sqre/mock-doc and
the packages are embedded in this repo's test_data/ directory.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import os
import tempfile
import shutil

import pkg_resources
import pytest
import sh
import ruamel.yaml

from ltdmason.product import Product
from ltdmason.manifest import Manifest


@pytest.fixture(scope='session')
def mock_manifest():
    """Provide the mock_manifest.yaml test file as a string."""
    resource_args = (__name__, 'mock_manifest.yaml')
    assert pkg_resources.resource_exists(*resource_args)
    yaml_str = pkg_resources.resource_string(*resource_args)

    # Patch the mock manifest to turn embedded package dir paths into
    # absolute paths
    yaml_data = ruamel.yaml.load(yaml_str)
    pkg_names = ('alpha', 'beta')
    test_dir = os.path.dirname(__file__)
    for n in pkg_names:
        p = os.path.join(test_dir, yaml_data['packages'][n]['dir'])
        yaml_data['packages'][n]['dir'] = p
    yaml_str = ruamel.yaml.dump(yaml_data)

    return yaml_str


@pytest.fixture(scope='session')
def product(request, mock_manifest):
    """Run the full product build pipeline.

    Since this fixture is session scoped it will only be run once; the tests
    then inspect the built product.

    The built documentation is automatically cleaned up with a finalizer.
    """
    build_dir = tempfile.mkdtemp()
    manifest = Manifest(mock_manifest)
    product = Product(manifest, build_dir)
    product.clone_doc_repo()
    product.link_package_repos()
    product.build_sphinx()

    def cleanup():
        shutil.rmtree(build_dir)
    request.addfinalizer(cleanup)

    return product


def test_clone_doc_repo(product):
    """Test how the doc repo was cloned."""
    manifest = product.manifest

    assert os.path.exists(product.doc_dir)
    # verify the correct ref is checked out
    git = sh.git.bake(_cwd=product.doc_dir)
    ref = str(git('symbolic-ref', 'HEAD').strip())
    print("doc repo ref:", ref, manifest.doc_repo_ref)
    assert ref.endswith(manifest.doc_repo_ref)


def test_link_package_repos(product):
    """Test links made from doc repo to package repos."""
    print(sh.ls('-al', product.doc_dir))

    for package_name, package_data in product.manifest.packages.items():
        print(package_name)
        # test that the package's directory exists in docs
        package_dir = os.path.join(product.build_dir,
                                   product.manifest.doc_repo_name,
                                   str(package_name))
        print(package_dir)
        assert os.path.isdir(package_dir)

        # test that the packages doc/_static directory is linked
        package_static_dir = os.path.join(package_data['dir'],
                                          'doc', '_static', package_name)
        if os.path.exists(package_static_dir):
            doc_package_static_dir = os.path.join(product.doc_dir,
                                                  '_static', str(package_name))
            assert os.path.islink(doc_package_static_dir)
            assert os.path.isdir(doc_package_static_dir)

        # test that individual entities of a package's doc (aside from _static)
        # are linked
        source_dir = os.path.join(package_data['dir'], 'doc')
        print('source_dir', source_dir)
        print(os.listdir(source_dir))
        target_dir = os.path.join(product.doc_dir, str(package_name))
        for entity in os.listdir(source_dir):
            print('entity', entity)
            if entity in product.package_excludes:
                continue
            link_name = os.path.join(target_dir, entity)
            assert os.path.islink(link_name)
            assert os.path.lexists(link_name)


def test_sphinx_build(product):
    assert os.path.exists(os.path.join(product.doc_dir, '_build', 'html'))
