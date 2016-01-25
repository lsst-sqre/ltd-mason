"""Interface for stack manifest YAML files written by buildlsstsw.sh

The purpose of these YAML files is to isolate ltd-mason from Eups/Scons
builds of the software itself and to merely tell ltd-mason where the built
software can be found, and metadata about the versioning of this Stack.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse
import os

import ruamel.yaml


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
        self.data = ruamel.yaml.load(f, ruamel.yaml.RoundTripLoader)

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
    def packages(self):
        """Dictionary of package names as keys and data as values.

        Package data is a dict with keys:

        - ``'dirname'``: directory where the package was installed by lsstsw.
        - ``'url'``: Git repository URL.
        - ``'ref'``: Git reference for package (branch, commit, tag).
        """
        return self.data['packages']
