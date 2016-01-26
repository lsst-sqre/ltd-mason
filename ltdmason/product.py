"""Includes the Product class, which coordinates a documentation build.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *
from future.standard_library import install_aliases
install_aliases()

import os

import sh

from .manifest import Manifest


class Product(object):
    """Representation of a documentation product, with logic and state
    for building a documentation project given a
    :class:`ltdmason.manifest.Manifest`.

    Parameters
    ----------
    manifest : :class:`ltdmason.manifest.Manifest`.
        A :class:`ltdmason.manifest.Manifest` instance that defines the
        documentation input.
    build_dir : str
        Directory where documentation will be built.
    """
    def __init__(self, manifest, build_dir):
        super().__init__()
        self.manifest = manifest
        self.build_dir = build_dir

    @property
    def doc_dir(self):
        """Directory path of the cloned documentation repository."""
        return os.path.join(self.build_dir, self.manifest.doc_repo_name)

    def clone_doc_repo(self):
        """Git clones the Sphinx documentation repository for this build
        product (specified in the :attr:`manifest`) into :attr:`build_dir`.
        """
        # Clone
        git_clone = sh.git.bake(_cwd=self.build_dir)
        git_clone.clone(self.manifest.doc_repo_url, self.doc_dir)

        # Checkout the appropriate ref
        git = sh.git.bake(_cwd=self.doc_dir)
        git.checkout(self.manifest.doc_repo_ref)

    def link_package_repos(self):
        """Link the doc/ directories of packages into the ``lsstsw``
        checked-out documunetation repository.

        The ``doc/_static/<pkgname>`` of each package is linked to the
        ``_static/<pkgname>/`` directory in the documentation repository.

        All other content of the package's ``doc/`` directory is linked into
        the ``<pkgname>/`` directory in the root of the documentation repo.
        """
        doc_static_dir = os.path.join(self.doc_dir, '_static')
        if not os.path.exists(doc_static_dir):
            os.makedirs(doc_static_dir)

        for package_name, package_data in self.manifest.packages.items():
            pkg_dir = str(package_data['dirname'])

            # Link _static/<pkgname>
            pkg_static_dir = os.path.join(pkg_dir, 'doc', '_static',
                                          package_name)
            try:
                os.symlink(pkg_static_dir,
                           os.path.join('_static', package_name))
            except OSError:
                # No package _static doc dir
                pass

            # Link all other entities in the doc/ directory to the package's
            # directory in the documentation repo
            target_doc_dir = os.path.join(self.doc_dir, package_name)
            if not os.path.exists(target_doc_dir):
                os.makedirs(target_doc_dir)
            source_doc_dir = os.path.join(pkg_dir, 'doc')
            # for root, dirs, files in os.walk('python/Lib/email'):
            for entity in os.listdir(source_doc_dir):
                if entity == '_static':
                    continue
                os.symlink(os.path.join(source_doc_dir, entity),
                           os.path.join(target_doc_dir, entity))

    def build_sphinx(self):
        """Run the Sphinx build process to produce HTML documentation."""
        pass
