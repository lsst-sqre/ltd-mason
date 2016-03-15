"""Upload built documentation to S3 and coordinate with ltd-keeper."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()

import logging

import requests

from .s3upload import upload


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def upload_via_keeper(manifest, product,
                      keeper_url, keeper_token,
                      aws_credentials=None):
    """Upload built documentation to S3 via ltd-keeper.

    This runs a three-step pipeline:

    1. Register the build on LTD Keeper with ``POST /products/<slug>/``
    2. Upload documentation files to an appropriate location (according to
       LTD Keeper) in an S3 bucket.
    3. Confirm to LTD Keeper that the documentation upload is complete.

    Parameters
    ----------
    manifest : :class:`ltdmason.manifest.Manifest`
        The manifest for the documentation build.
    product : :class:`ltdmason.product.Product`
        The :class:`~ltdmason.product.Product` that built the documentation.
    keeper_url : str
        URL of the ltd-keeper HTTP API service.
    keeper_token : str
        Authorization token for the ltd-keeper instance.
    aws_credentials : dict, optional
        A `dict` specifying an AWS credential configuration. There are three
        variants:

        1. Leave unset to rely on defaults in :file:`~/.aws/credentials`::

        2. Runtime-specified credentials (perhaps through ltd-mason environment
           variables)::

              {'aws_access_key_id': '...',
               'aws_secret_access_key': '...'}

        3. Runtime-specific name of a profile of credentials stored in
           :file:`~/.aws/credentials`::

              {'aws_profile': '...'}

        See http://boto3.readthedocs.org/en/latest/guide/configuration.html
        for information on :file:`~/.aws/credentials`.

    Raises
    ------
    KeeperError
       Any anomaly with LTD Keeper interaction.
    """
    # Register the documentation build for this product
    build_resource = _register_build(manifest, keeper_url, keeper_token)
    build_url = build_resource['self_url']

    # Upload documentation site to S3
    if aws_credentials is None:
        # Fall back to using default AWS credentials the user might have set
        aws_credentials = {}
    upload(build_info['bucket_name'],
           build_info['bucket_root_dir'],
           product.html_dir,
           **aws_credentials)
    log.debug('Upload complete: {0}:{1}'.format(
        build_info['bucket_name'], build_info['bucket_root_dir']))

    # Confirm upload to ltd-keeper
    _confirm_upload(build_url, keeper_token)


def _register_build(manifest, keeper_url, keeper_token):
    """Register this documentation build with LTD Keeper

    This registration step tells ltd-mason where to upload the documentation
    files (bucket and directory).

    Raises
    ------
    KeeperError
       Any anomaly with LTD Keeper interaction.
    """
    r = requests.post(
        keeper_url + '/products/{p}/builds/'.format(
            p=manifest.product_name),
        auth=(keeper_token, ''),
        json={'slug': manifest.build_id,
              'git_refs': manifest.refs,
              'github_requester': manifest.requester_github_handle})
    if r.status_code != 201:
        raise KeeperError(r.json())
    build_info = r.json()
    log.debug(r.json())
    return build_info


def _confirm_upload(build_url, keeper_token):
    """Patch the build on LTD Keeper to say that the upload is successful.

    Raises
    ------
    KeeperError
       Any anomaly with LTD Keeper interaction.
    """
    r = requests.patch(build_url,
                       auth=(keeper_token, ''),
                       json={'uploaded': True})
    if r.status_code != 200:
        raise KeeperError(r)
    log.debug(r.json())


class KeeperError(Exception):
    """Error using the LTD Keeper API."""
    pass
