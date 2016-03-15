"""Interface for stack manifest YAML files written by buildlsstsw.sh

The purpose of these YAML files is to isolate ltd-mason from Eups/Scons
builds of the software itself and to merely tell ltd-mason where the built
software can be found, and metadata about the versioning of this Stack.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse
import os

import jsonschema
import ruamel.yaml
import pkg_resources


class Manifest(object):
    """Representation of a YAML-encoded manifest for an LSST stack product.

    Parameters
    ----------
    yaml_data : str
        Stack manifest, encoded as YAML text.

    Attributes
    ----------
    data : `ruamel.yaml` object
        Manifest dataset loaded by :mod:`ruamel.yamel`.
    """
    def __init__(self, f):
        super().__init__()
        data = ruamel.yaml.load(f, ruamel.yaml.RoundTripLoader)
        Manifest.validate(data)
        self.data = data

    @property
    def yaml(self):
        """YAML representation of the manifest (:class:`str`)."""
        return ruamel.yaml.dump(self.data, Dumper=ruamel.yaml.RoundTripDumper)

    @property
    def doc_repo_url(self):
        """Git URL for the product's Git documentation repository."""
        return self.data['doc_repo']['url']

    @property
    def doc_repo_ref(self):
        """Git ref (branch, commit, tag) for the product's Git documentation
        repository (:class:`str`).
        """
        return self.data['doc_repo']['ref']

    @property
    def doc_repo_name(self):
        """Name of the product's Git documentation repository (:class:`str`).

        For example, a doc repository at
        ``'https://github.com/lsst-sqre/pipelines_doc.git'`` is named
        ``'pipelines_doc'``.
        """
        parts = urlparse(self.doc_repo_url)
        return os.path.splitext(parts.path)[0].split('/')[-1]

    @property
    def product_name(self):
        """Name of the documentation product."""
        return self.data['product_name']

    @property
    def build_id(self):
        """Build identifier (`str`)."""
        return self.data['build_id']

    @property
    def requester_github_handle(self):
        """GitHub username handle of person who triggered the build. `None`
        if not available.
        """
        if 'requester_github_handle' in self.data:
            return self.data['requester_github_handle']
        else:
            return None

    @property
    def refs(self):
        """`list` of Git refs that define the overal version set of the
        products.
        """
        return self.data['refs']

    @property
    def packages(self):
        """Dictionary of package names as keys and package data as values.

        Package data is a dict with keys:

        - ``'dir'``: directory where the package was installed by lsstsw. This
          is ensured to be an absolute URL, transforming any relative paths
          in the Manifest, assuming they are relative to the **current
          working directory.**
        - ``'url'``: Git repository URL.
        - ``'ref'``: Git reference for package (branch, commit, tag).
        """
        data = {}
        for pkg_name, pkg_data in self.data['packages'].items():
            pkg_data = dict(pkg_data)
            pkg_data['dir'] = os.path.abspath(pkg_data['dir'])
            data[pkg_name] = pkg_data
        return data

    @classmethod
    def validate(self, data):
        """Validate the schema of a parsed YAML manifest."""
        schema = load_manifest_schema()
        jsonschema.validate(data, schema)


def load_manifest_schema():
    resource_args = (__name__, '../manifest_schema.yaml')
    assert pkg_resources.resource_exists(*resource_args)
    yaml_data = pkg_resources.resource_string(*resource_args)
    return ruamel.yaml.load(yaml_data)
