"""Command line interface for ltd-mason that runs a doc build."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()

import os
import argparse
import textwrap
import sys
from io import open
import tempfile
import shutil
import logging

import ruamel.yaml
import requests

from .manifest import Manifest
from .product import Product
from .uploader import upload_via_keeper


def run_ltd_mason():
    """Command line app: ``ltd-mason``.

    This app is intended to be called from ``buildlsstsw.sh`` and is
    responsible for running the full documentation build and upload
    process.
    """
    logging.basicConfig(level=logging.INFO)
    args, unknown_args = parse_args()
    if args.manifest_path is None:
        # Read manifest from stdin
        manifest_data = sys.stdin.read()
    else:
        # Read manifest from file
        with open(args.manifest_path, mode='r', encoding='utf-8') as f:
            manifest_data = f.read()
    manifest = Manifest(manifest_data)

    if args.build_dir is None:
        # Use a temporary directory by default
        build_dir = tempfile.mkdtemp()
    else:
        # Use a debug directory
        build_dir = os.path.abspath(args.build_dir)
        assert build_dir is not os.getcwd(), "--build-dir can't be CWD"
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.makedirs(build_dir)

    product = Product(manifest, build_dir)
    product.clone_doc_repo()
    product.link_package_repos()
    product.install_dependencies()
    product.build_sphinx()

    if not args.no_upload:
        configs = read_configs(args.config_path)
        keeper_token = get_keeper_token(configs['keeper_url'],
                                        configs['keeper_username'],
                                        configs['keeper_password'])
        upload_via_keeper(manifest, product,
                          configs['keeper_url'], keeper_token,
                          configs['aws_profile'])

    if args.build_dir is None:
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
               keeper_username: '<username for ltd-keeper instance>'
               keeper_password: '<password for ltd-keeper instance>'
               aws_profile: '<AWS profile in ~/.aws/credentials>'

            See the Boto3 config guide (http://bit.ly/1WuF7rY) for info
            on adding your AWS credentials.
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
    parser.add_argument(
        '--no-upload',
        dest='no_upload',
        default=False,
        action='store_true',
        help='Skip the upload to S3 and ltd-keeper; only build the docs')
    parser.add_argument(
        '--build-dir',
        default=None,
        dest='build_dir',
        help='Directory to use for building the documentation. By default a '
             'temporary directory is created an deleted. This manually-set '
             'directory is not deleted to aid debugging. Beware that any '
             'existing content in that directory will be deleted.')
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

    if 'keeper_username' not in config_data:
        raise RuntimeError('No config {0} in {1}'.format(
            'keeper_username', config_path))

    if 'keeper_password' not in config_data:
        raise RuntimeError('No config {0} in {1}'.format(
            'keeper_password', config_path))

    if 'aws_profile' not in config_data:
        # Assume default profile
        config_data['aws_profile'] = 'default'

    return config_data


def get_keeper_token(base_url, username, password):
    """Get a temporary auth token from ltd-keeper."""
    token_endpoint = base_url + '/token'
    r = requests.get(token_endpoint, auth=(username, password))
    if r.status_code != 200:
        raise RuntimeError('Could not authenticate to {0}: error {1:d}\n{2}'.
                           format(base_url, r.status_code, r.json()))
    return r.json()['token']
