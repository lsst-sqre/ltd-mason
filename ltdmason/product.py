"""Includes the Product class, which coordinates a documentation build.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import os
import logging
from io import BytesIO
import abc

import sh

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BaseProduct(object):
    """Abstract base class specifying the minimum API for products classes."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def html_dir(self):
        """Directory path of the built HTML product."""
        return

    @abc.abstractproperty
    def doc_dir(self):
        """Directory path of the cloned documentation repository."""
        pass


class Product(BaseProduct):
    """Representation of a documentation product, with logic and state
    for building a documentation project given a
    :class:`ltdmason.manifest.Manifest`. This is intended for Eups-based
    documentation builds from a Jenkins environment.

    Parameters
    ----------
    manifest : :class:`ltdmason.manifest.Manifest`.
        A :class:`ltdmason.manifest.Manifest` instance that defines the
        documentation input.
    build_dir : str
        Directory where documentation will be built.
    """
    # Package directories/files that won't get linked into product doc repo
    # Note that _static/ is handled separately
    package_excludes = ['_static', '_build', '_templates', 'conf.py', '.git']

    def __init__(self, manifest, build_dir):
        super().__init__()
        self.manifest = manifest
        self.build_dir = build_dir

    @property
    def doc_dir(self):
        """Directory path of the cloned documentation repository."""
        return os.path.join(self.build_dir, self.manifest.doc_repo_name)

    @property
    def html_dir(self):
        """Directory path of the built HTML product."""
        return os.path.join(self.doc_dir, '_build', 'html')

    def clone_doc_repo(self):
        """Git clones the Sphinx documentation repository for this build
        product (specified in the :attr:`manifest`) into :attr:`build_dir`.
        """
        # Clone
        clone_out_log = BytesIO()
        clone_err_log = BytesIO()
        git_clone = sh.git.bake(_cwd=self.build_dir)
        git_clone.clone(self.manifest.doc_repo_url, self.doc_dir,
                        _out=clone_out_log,
                        _err=clone_err_log)
        log.debug(clone_out_log.getvalue())
        log.debug(clone_err_log.getvalue())

        # Checkout the appropriate ref
        checkout_out_log = BytesIO()
        checkout_err_log = BytesIO()
        git = sh.git.bake(_cwd=self.doc_dir)
        git.checkout(self.manifest.doc_repo_ref,
                     _out=checkout_out_log,
                     _err=checkout_err_log)
        log.debug(checkout_out_log.getvalue())
        log.debug(checkout_err_log.getvalue())

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
            pkg_dir = str(package_data['dir'])

            # validate that the package's doc directory exists; skip if not
            source_doc_dir = os.path.join(pkg_dir, 'doc')
            if not os.path.isdir(source_doc_dir):
                log.debug(
                    'Skipping {0}: no doc/ directory'.format(package_name))
                continue

            # Link _static/<pkgname>
            source_static_dir = os.path.join(source_doc_dir, '_static',
                                             package_name)
            if not os.path.isdir(source_static_dir):
                log.debug(
                    'No _static/ directory found for {0}; skipping'
                    .format(package_name))
            else:
                target = os.path.join(self.doc_dir, '_static', package_name)
                log.debug(
                    'Linking {0} to {1}'.format(source_static_dir, target))
                os.symlink(source_static_dir, target)

            # Link all other entities in the doc/ directory to the package's
            # directory in the documentation repo
            target_doc_dir = os.path.join(self.doc_dir, package_name)
            if not os.path.exists(target_doc_dir):
                os.makedirs(target_doc_dir)
            for entity in os.listdir(source_doc_dir):
                if entity in self.package_excludes:
                    # skips protected dirs like _build, _templates, _static
                    # _static is linked separately, above
                    continue
                src = os.path.join(source_doc_dir, entity)
                target = os.path.join(target_doc_dir, entity)
                log.debug('Linking {0} to {1}'.format(src, target))
                os.symlink(src, target)

    def install_dependencies(self):
        """Install dependencies specific in the doc repo's requirements.txt"""
        if os.path.exists(os.path.join(self.doc_dir, 'requirements.txt')):
            pip_out_log = BytesIO()
            pip_err_log = BytesIO()
            pip = sh.pip.bake(_cwd=self.doc_dir)
            pip.install('-r', 'requirements.txt',
                        _out=pip_out_log,
                        _err=pip_err_log)
            log.debug(pip_out_log.getvalue())
            log.debug(pip_err_log.getvalue())

    def build_sphinx(self):
        """Run the Sphinx build process to produce HTML documentation.

        This method calls ``sphinx-build``, which is installed by Sphinx.
        """
        builder = sh.Command('sphinx-build')
        build_out_log = BytesIO()
        build_err_log = BytesIO()
        builder(self.doc_dir, self.html_dir,
                b='html',  # HTML builder
                a=True,  # build all, without caching
                _out=build_out_log,
                _err=build_err_log)
        log.debug(build_out_log.getvalue())
        log.debug(build_err_log.getvalue())


class TravisProduct(BaseProduct):
    """Representation of a documentation product in the Travis environment.

    This product assuemes the doc project has been cloned and build natively
    by Travis; this product merely reports the build directory to the
    uploader.
    """
    def __init__(self, html_dir):
        super(TravisProduct, self).__init__()
        self._html_dir = html_dir

    @property
    def html_dir(self):
        """Directory path of the built HTML product."""
        return self._html_dir

    @property
    def doc_dir(self):
        # LTD Mason on Travis doesn't need to know about the Sphinx repo
        # since it isn't building sphinx.
        raise NotImplementedError
