"""Command line interface for ltd-mason that runs a doc build."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()

import argparse
import textwrap
import sys
from io import open
import tempfile
import shutil

import ruamel.yaml

from .manifest import Manifest
from .product import Product


def run_ltd_mason():
    """Command line app: ``ltd-mason``.

    This app is intended to be called from ``buildlsstsw.sh`` and is
    responsible for running the full documentation build and upload
    process.
    """
    args, unknown_args = parse_args()
    if args.manifest_path is None:
        # Read manifest from stdin
        manifest_data = sys.stdin.read()
    else:
        # Read manifest from file
        with open(args.manifest_path, mode='r', encoding='utf-8') as f:
            manifest_data = f.read()
    manifest = Manifest(manifest_data)

    configs = read_configs(args.config_path)

    # FIXME replace with a context
    build_dir = tempfile.mkdtemp()

    product = Product(manifest, build_dir)
    product.clone_doc_repo()
    product.link_package_repos()
    product.build_sphinx()

    shutil.rmtree(build_dir)


def parse_args():
    """Create an ``argparse.ArgumentParser`` instance that define's ltd-mason's
    command line interface.
    """
    parser = argparse.ArgumentParser(
        prog='ltd-mason',
        description=textwrap.dedent("""
            Build Sphinx product documentation for LSST the Docs.

            ltd-mason is driven by a YAML-formatted manifest file. The manifest
            can either be provided as a file using the `--manifest` argument,

            ltd-mason --manifest manifest.yaml

            or piped in,

            cat manifest.yaml | ltd-mason

            ltd-mason also expects a configuration file (for working with the
            ltd-keeper documentation coordinater. The configuration file is
            YAML-formatted with fields

               keeper_url: '<URL of ltd-keeper instance>'
               keeper_token: '<auth token from ltd-keeper instance>'
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='See https://github.com/lsst-sqre/ltd-mason')
    parser.add_argument(
        '--manifest',
        dest='manifest_path',
        default=None,
        help='Path to YAML manifest file that defines the doc build.')
    parser.add_argument(
        '--config',
        dest='config_path',
        help='Path to ltd-mason configuration file (default `~/.ltdmason`)')
    args, unknown_args = parser.parse_known_args()
    return args, unknown_args


def read_configs(config_path):
    """Read a YAML file with ltd-mason configurations."""
    try:
        with open(config_path, mode='r', encoding='utf-8') as f:
            config_data = ruamel.yaml.load(f)
    except OSError:
        raise OSError('Could not read configuration file at {0}'.format(
            config_path))

    if 'keeper_url' not in config_data:
        raise RuntimeError('No config {0} in {1}'.format(
            'keeper_url', config_path))

    if 'keeper_token' not in config_data:
        raise RuntimeError('No config {0} in {1}'.format(
            'keeper_token', config_path))

    return config_data
