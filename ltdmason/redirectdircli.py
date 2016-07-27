"""Command line interface to add directory redirect objects.
"""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA


import argparse
import os
import textwrap
import logging

import boto3

from .s3upload import _upload_object


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def run():
    """Entrypoint for ltd-mason-make-redirects."""
    args = parse_args()

    logging.basicConfig(level=logging.INFO)

    # create a bucket object
    session = boto3.session.Session(
        aws_access_key_id=args.aws_id,
        aws_secret_access_key=args.aws_secret)
    s3 = session.resource('s3')
    bucket = s3.Bucket(args.bucket)

    directories = []
    for obj in bucket.objects.filter(Prefix=args.base_dir):
        dirname = os.path.dirname(obj.key)
        if dirname:
            directories.append(dirname)
    directories = set(directories)
    for dirname in directories:
        if dirname.endswith('/v') or dirname.endswith('/builds'):
            # Skip {product}/v or {product}/builds directories
            continue
        # create a directory redirect object
        redirect_metadata = {'dir-redirect': 'true'}
        cache_control = 'max-age={0}'.format(31536000)
        logging.info('Making redirect object at {0}'.format(dirname))
        if not args.dry_run:
            _upload_object(dirname,
                           content='',
                           bucket=bucket,
                           metadata=redirect_metadata,
                           acl='public-read',
                           cache_control=cache_control)


def parse_args():
    """Create an ``argparse.ArgumentParser`` instance that defines the
    command line interface for ltd-mason-make-directs.
    """
    parser = argparse.ArgumentParser(
        prog='ltd-mason-make-redirects',
        description=textwrap.dedent("""Bulk-add directory courtesy redirect
objects to an existing LSST the Docs bucket.

These redirect objects are named after directories (without a trailing slash)
and contain an ``x-amx-meta-dir-redirect=true`` HTTP header. The Fastly VCL
code detects when these objects are being requested (e.g. example.com/dir)
and issues a 301 redirect to example.com/dir/index.html).

This script should only be run once to add redirects to existing
builds. The regular ltd-mason and ltd-keeper workflows will maintain redirects
subsequently.
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='See https://github.com/lsst-sqre/ltd-mason for more info.')
    parser.add_argument(
        '--bucket',
        help='LSST the Docs S3 bucket',
        required=True)
    parser.add_argument(
        '--base-dir',
        help='Directory to make redirects in (defaults to all directories)',
        default='')
    parser.add_argument(
        '--aws-id',
        help='AWS access key ID',
        required=True)
    parser.add_argument(
        '--aws-secret',
        help='AWS secret access key',
        required=True)
    parser.add_argument(
        '--dry-run',
        help='Dry-run, prevents objects from being uploaded',
        action='store_true',
        default=False)
    return parser.parse_args()
