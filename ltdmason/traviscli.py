"""Command line interface for ltd-mason specialized for Travis CI-based builds.
"""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import sys
import os
import logging
import argparse
import textwrap

from .manifest import TravisManifest
from .product import TravisProduct
from .uploader import upload


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def run():
    """Entrypoint for ltd-mason-travis command."""
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Only build when the env var 'LTD_MASON_BUILD' is set to True
    # This is useful for Travis build matrices; we want to specify
    # exactly which test run to run Mason on.
    mason_build_flag = os.getenv('LTD_MASON_BUILD')
    if mason_build_flag is None:
        log.info('ltd-mason-travis skipping build')
        sys.exit(0)
    elif mason_build_flag.lower() != 'true':
        log.info('ltd-mason-travis skipping build')
        sys.exit(0)

    # Verify this is a branch build on Travis; not a PR build.
    travis_pr_flag = os.getenv('TRAVIS_PULL_REQUEST')
    if travis_pr_flag is None:
        raise RuntimeError(
            'TRAVIS_PULL_REQUEST environment variable not found')
    if travis_pr_flag.lower() != 'false':
        # Silently exit so as not to disturb a Travis CI of code tests
        log.info('ltd-mason-travis skipping PR build')
        sys.exit(0)

    manifest = TravisManifest()
    product = TravisProduct(os.path.abspath(os.path.expandvars(args.html_dir)))

    if not args.no_upload:
        upload(manifest, product)


def parse_args():
    """Create an ``argparse.ArgumentParser`` instance that define's ltd-mason's
    command line interface.
    """
    parser = argparse.ArgumentParser(
        prog='ltd-mason-travis',
        description=textwrap.dedent("""
            Build Sphinx product documentation for LSST the Docs.

            ltd-mason-travis is intended to be run from a Travis CI
            environment. Travis should build the Sphinx document. Tell Mason
            where the built HTML is located with the --html-dir argument.

            ltd-mason-travis uses environment variables for configuration:

            LTD_MASON_BUILD
               Set to `true` to declare a build should be run with Mason.
               In a Travis CI build matrix, only one build should run Mason.

            LTD_MASON_PRODUCT
               Name of the LSST the Docs product.

            LTD_MASON_AWS_ID
               AWS access key ID.

            LTD_MASON_AWS_SECRET
               AWS secret access key.

            Note that the AWS credentials specified here must have permission
            to read and write into the S3 buckets managed by the LTD Keeper
            server.

            LTD_KEEPER_URL
               URL of LTD Keeper instance.

            LTD_KEEPER_USER
               Username for LTD Keeper instance.

            LTD_KEEPER_PASSWORD
               Password for LTD Keeper instance.

            ltd-mason-travis also assumes that the following environment
            variables are available in a Travis environment:

            TRAVIS_PULL_REQUEST
               If true, then ltd-mason-travis will exit. Only branch-based
               builds are supported.

            TRAVIS_REPO_SLUG
               To identify the source Git repository (assuming it resides on
               GitHub.

            TRAVIS_BRANCH
               To identify the branch that is being build to associate this
               build with an Edition on LSST the Docs.
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='See https://github.com/lsst-sqre/ltd-mason for more info.')
    parser.add_argument(
        '--html-dir',
        dest='html_dir',
        default='',
        help='Directory of the built HTML site')
    parser.add_argument(
        '--no-upload',
        dest='no_upload',
        default=False,
        action='store_true',
        help='Skip the upload to S3 and ltd-keeper')
    parser.add_argument(
        '--verbose',
        dest='verbose',
        default=False,
        action='store_true',
        help='Full logging of debug messages')
    return parser.parse_args()
