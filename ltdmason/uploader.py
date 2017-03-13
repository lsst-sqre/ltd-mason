"""Upload built documentation to S3 and coordinate with ltd-keeper."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import os
import logging

import requests

# weird import helps with mocking
from .s3upload import upload as s3upload_upload


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def upload(manifest, product):
    aws_credentials = read_aws_credentials()
    keeper_credentials = read_keeper_credentials()
    keeper_token = get_keeper_token(
        keeper_credentials['keeper_url'],
        keeper_credentials['keeper_username'],
        keeper_credentials['keeper_password'])
    upload_via_keeper(manifest, product,
                      keeper_url=keeper_credentials['keeper_url'],
                      keeper_token=keeper_token,
                      aws_credentials=aws_credentials)


def read_aws_credentials():
    keys = (('aws_profile', 'LTD_MASON_AWS_PROFILE'),
            ('aws_access_key_id', 'LTD_MASON_AWS_ID'),
            ('aws_secret_access_key', 'LTD_MASON_AWS_SECRET'))
    c = {k: os.getenv(envvar) for (k, envvar) in keys}
    if c['aws_access_key_id'] is not None \
            and c['aws_secret_access_key'] is not None:
        del c['aws_profile']
        log.debug('Using $LTD_MASON_AWS_ID and $LTD_MASON_AWS_SECRET')
    else:
        del c['aws_access_key_id']
        del c['aws_secret_access_key']
        if c['aws_profile'] is None:
            log.debug('Assuming default AWS credential setup')
            del c['aws_profile']
        else:
            log.debug('Using $LTD_MASON_AWS_PROFILE')

    return c


def read_keeper_credentials():
    keys = (('keeper_url', 'LTD_KEEPER_URL'),
            ('keeper_username', 'LTD_KEEPER_USER'),
            ('keeper_password', 'LTD_KEEPER_PASSWORD'))
    c = {k: os.getenv(envvar) for (k, envvar) in keys}
    for (k, envvar) in keys:
        if c[k] is None:
            raise RuntimeError('Please set {0}'.format(envvar))
    return c


def get_keeper_token(base_url, username, password):
    """Get a temporary auth token from ltd-keeper."""
    token_endpoint = base_url + '/token'
    r = requests.get(token_endpoint, auth=(username, password))
    if r.status_code != 200:
        raise RuntimeError('Could not authenticate to {0}: error {1:d}\n{2}'.
                           format(base_url, r.status_code, r.json()))
    return r.json()['token']


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

    # Upload documentation site to S3
    if aws_credentials is None:
        # Fall back to using default AWS credentials the user might have set
        aws_credentials = {}
    s3upload_upload(build_resource['bucket_name'],
                    build_resource['bucket_root_dir'],
                    product.html_dir,
                    surrogate_key=build_resource['surrogate_key'],
                    acl=None,
                    cache_control_max_age=31536000,
                    **aws_credentials)
    log.debug('Upload complete: {0}:{1}'.format(
        build_resource['bucket_name'], build_resource['bucket_root_dir']))

    # Confirm upload to ltd-keeper
    _confirm_upload(build_resource['self_url'], keeper_token)


def _register_build(manifest, keeper_url, keeper_token):
    """Register this documentation build with LTD Keeper

    This registration step tells ltd-mason where to upload the documentation
    files (bucket and directory).

    Raises
    ------
    KeeperError
       Any anomaly with LTD Keeper interaction.
    """
    data = {'git_refs': manifest.refs}
    if manifest.build_id is not None:
        data['slug'] = manifest.build_id
    if manifest.requester_github_handle is not None:
        data['github_requester'] = manifest.requester_github_handle

    r = requests.post(
        keeper_url + '/products/{p}/builds/'.format(
            p=manifest.product_name),
        auth=(keeper_token, ''),
        json=data)

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
