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


def upload_via_keeper(manifest, product, keeper_url, keeper_token):
    """Upload built documentation to S3 via ltd-keeper.

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
    """
    # Register the documentation build for this product
    r = requests.post(
        keeper_url + '/v1/products/{p}/builds/'.format(
            p=manifest.product_name),
        auth=(keeper_token, ''),
        json={'slug': manifest.build_id,
              'git_refs': manifest.refs,
              'github_requester': manifest.requester_github_handle})
    if r.status_code != 201:
        raise KeeperError(r.json())
    build_info = r.json()
    build_url = build_info['self_url']
    log.info(r.json())

    # Upload documentation site to S3
    upload(build_info['bucket_name'],
           build_info['bucket_root_dir'],
           product.html_dir)
    log.info('Upload complete: {0}:{1}'.format(
        build_info['bucket_name'], build_info['bucket_root_dir']))

    # Confirm upload to ltd-keeper
    r = requests.post(
        build_url + '/uploaded',
        auth=(keeper_token, ''))
    if r.status_code != 202:
        raise KeeperError(r.json())
    log.info(r.json())


class KeeperError(Exception):
    """Error using the LTD Keeper API."""
    pass
