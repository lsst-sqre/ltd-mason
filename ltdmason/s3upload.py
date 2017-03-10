"""S3 upload/sync utilities."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import os
import logging
import mimetypes

import boto3

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def upload(bucket_name, path_prefix, source_dir,
           upload_dir_redirect_objects=True,
           surrogate_key=None, acl=None,
           cache_control_max_age=31536000,
           aws_access_key_id=None, aws_secret_access_key=None,
           aws_profile=None):
    """Upload built documentation to S3.

    This function places the contents of the Sphinx HTML build directory
    into the ``/path_prefix/`` directory of an *existing* S3 bucket.
    Existing files on S3 are overwritten; files that no longer exist in the
    ``source_dir`` are deleted from S3.

    S3 credentials are assumed to be stored in a place where boto3 can read
    them, such as :file:`~/.aws/credentials`. `aws_profile_name` allows you
    to select while AWS credential profile you wish to use from the
    :file:`~/.aws/credentials`.
    See http://boto3.readthedocs.org/en/latest/guide/quickstart.html.

    Parameters
    ----------
    bucket_name : str
        Name of the S3 bucket where documentation is uploaded.
    path_prefix : str
        The root directory in the bucket where documentation is stored.
    source_dir : str
        Path of the Sphinx HTML build directory on the local file system.
        The contents of this directory are uploaded into the ``/path_prefix/``
        directory of the S3 bucket.
    upload_dir_redirect_objects : bool, optional
        A feature flag to enable uploading objects to S3 for every directory.
        These objects contain headers ``x-amz-meta-dir-redirect=true`` HTTP
        headers that tell Fastly to issue a 301 redirect from the directory
        object to the '/index.html' in that directory.
    surrogate_key : str, optional
        The surrogate key to insert in the header of all objects
        in the ``x-amz-meta-surrogate-key`` field. This key is used to purge
        builds from the Fastly CDN when Editions change.
        If `None` then no header will be set.
    acl : str, optional
        The pre-canned AWS access control list to apply to this upload.
        Defaults to ``'public-read'``, which allow files to be downloaded
        over HTTP by the public. See
        https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
        for an overview of S3's pre-canned ACL lists. Note that ACL settings
        are not validated locally.
    cache_control_max_age : int, optional
        Defaults to 31536000 seconds = 1 year.
    aws_access_key_id : str, optional
        The access key for your AWS account. Also set `aws_secret_access_key`.
    aws_secret_access_key : str, optional
        The secret key for your AWS account.
    aws_profile : str, optional
        Name of AWS profile in :file:`~/.aws/credentials`. Use this instead
        of `aws_access_key_id` and `aws_secret_access_key` for file-based
        credentials.
    """
    log.debug('s3upload.upload({0}, {1}, {2})'.format(
        bucket_name, path_prefix, source_dir))

    session = boto3.session.Session(
        profile_name=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    metadata = None
    if surrogate_key is not None:
        if metadata is None:
            metadata = {}
        metadata['surrogate-key'] = surrogate_key

    if cache_control_max_age is not None:
        cache_control = 'max-age={0:d}'.format(cache_control_max_age)
    else:
        cache_control = None

    manager = ObjectManager(session, bucket_name, path_prefix)

    for (rootdir, dirnames, filenames) in os.walk(source_dir):
        # name of root directory on S3 bucket
        bucket_root = os.path.relpath(rootdir, start=source_dir)
        if bucket_root in ('.', '/'):
            bucket_root = ''

        # Delete bucket directories that no longer exist in source
        bucket_dirnames = manager.list_dirnames_in_directory(bucket_root)
        for bucket_dirname in bucket_dirnames:
            if bucket_dirname not in dirnames:
                log.debug(('Deleting bucket directory {0}'.format(
                    bucket_dirname)))
                manager.delete_directory(bucket_dirname)

        # Delete files that no longer exist in source
        bucket_filenames = manager.list_filenames_in_directory(bucket_root)
        for bucket_filename in bucket_filenames:
            if bucket_filename not in filenames:
                bucket_filename = os.path.join(bucket_root, bucket_filename)
                log.debug('Deleting bucket file {0}'.format(bucket_filename))
                manager.delete_file(bucket_filename)

        # Upload files in directory
        for filename in filenames:
            local_path = os.path.join(rootdir, filename)
            bucket_path = os.path.join(path_prefix, bucket_root, filename)
            log.debug('Uploading to {0}'.format(bucket_path))
            _upload_file(local_path, bucket_path, bucket,
                         metadata=metadata, acl=acl,
                         cache_control=cache_control)

        # Upload a directory redirect object
        if upload_dir_redirect_objects is True:
            bucket_dir_path = os.path.join(path_prefix, bucket_root)
            bucket_dir_path = bucket_dir_path.rstrip('/')
            if metadata:
                redirect_metadata = dict(metadata)
            else:
                redirect_metadata = {}
            redirect_metadata['dir-redirect'] = 'true'
            _upload_object(bucket_dir_path,
                           content='',
                           bucket=bucket,
                           metadata=redirect_metadata,
                           acl=acl,
                           cache_control=cache_control)


def _upload_file(local_path, bucket_path, bucket,
                 metadata=None, acl=None, cache_control=None):
    """Upload a file to the S3 bucket.

    This function uses the mimetypes module to guess and then set the
    Content-Type and Encoding-Type headers.

    Parameters
    ----------
    local_path : str
        Full path to a file on the local file system.
    bucket_path : str
        Destination path (also known as the key name) of the file in the
        S3 bucket.
    bucket : `boto3` Bucket instance
        S3 bucket.
    metadata : dict, optional
        Header metadata values. These keys will appear in headers as
        ``x-amz-meta-*``.
    acl : str, optional
        A pre-canned access control list. See
        https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
    cache_control : str, optional
        The cache-control header value. For example, 'max-age=31536000'.
        ``'
    """
    extra_args = {}
    if acl is not None:
        extra_args['ACL'] = acl
    if metadata is not None:
        extra_args['Metadata'] = metadata
    if cache_control is not None:
        extra_args['CacheControl'] = cache_control

    # guess_type returns None if it cannot detect a type
    content_type, content_encoding = mimetypes.guess_type(local_path,
                                                          strict=False)
    if content_type is not None:
        extra_args['ContentType'] = content_type

    log.debug(str(extra_args))

    obj = bucket.Object(bucket_path)
    # no return status from the upload_file api
    obj.upload_file(local_path, ExtraArgs=extra_args)


def _upload_object(bucket_path, bucket, content='',
                   metadata=None, acl=None, cache_control=None):
    """Upload an arbitrary object to an S3 bucket.

    Parameters
    ----------
    bucket_path : str
        Destination path (also known as the key name) of the file in the
        S3 bucket.
    content : str or bytes
        Object content, optional
    bucket : `boto3` Bucket instance
        S3 bucket.
    metadata : dict, optional
        Header metadata values. These keys will appear in headers as
        ``x-amz-meta-*``.
    acl : str, optional
        A pre-canned access control list. See
        https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
    cache_control : str, optional
        The cache-control header value. For example, 'max-age=31536000'.
        ``'
    """
    args = {}
    if metadata is not None:
        args['Metadata'] = metadata
    if acl is not None:
        args['ACL'] = acl
    if cache_control is not None:
        args['CacheControl'] = cache_control
    obj = bucket.Object(bucket_path)
    obj.put(Body=content, **args)


class ObjectManager(object):
    """Manage objects existing in a bucket under a specific ``bucket_root``.

    The ObjectManager maintains information about objects that exist in the
    bucket, and can delete objects that no longer exist in the source.

    Parameters
    ----------
    session : :class:`boto3.session.Session`
        A boto3 session instance provisioned with the correct identities.
    bucket_name : str
        Name of the S3 bucket.
    bucket_root : str
        The version slug is the name root directory in the bucket where
        documentation is stored.
    """
    def __init__(self, session, bucket_name, bucket_root):
        super().__init__()
        s3 = session.resource('s3')
        bucket = s3.Bucket(bucket_name)
        self._session = session
        self._bucket = bucket
        self._bucket_root = bucket_root
        # Strip trailing '/' from bucket_root for comparisons
        if self._bucket_root.endswith('/'):
            self._bucket_root = self._bucket_root.rstrip('/')

    def list_filenames_in_directory(self, dirname):
        """List all file-type object names that exist at the root of this
        bucket directory.

        Parameters
        ----------
        dirname : str
            Directory name in the bucket relative to ``bucket_root/``.

        Returns
        -------
        filenames : list
            List of file names (`str`), relative to ``bucket_root/``, that
            exist at the root of ``dirname``.
        """
        prefix = self._create_prefix(dirname)
        filenames = []
        for obj in self._bucket.objects.filter(Prefix=prefix):
            if obj.key.endswith('/'):
                continue
            obj_dirname = os.path.dirname(obj.key)
            if obj_dirname == prefix:
                # object is at root of directory
                filenames.append(os.path.relpath(obj.key,
                                                 start=prefix))
        return filenames

    def list_dirnames_in_directory(self, dirname):
        """List all names of directories that exist at the root of this
        bucket directory.

        Note that *directories* don't exist in S3; rather directories are
        inferred from path names.

        Parameters
        ----------
        dirname : str
            Directory name in the bucket relative to ``bucket_root``.

        Returns
        -------
        dirnames : list
            List of directory names (`str`), relative to ``bucket_root/``,
            that exist at the root of ``dirname``.
        """
        prefix = self._create_prefix(dirname)
        dirnames = []
        for obj in self._bucket.objects.filter(Prefix=prefix):
            dirname = os.path.dirname(obj.key)
            # if the object is a directory redirect, make it look like a dir
            if dirname == '':
                dirname = obj.key + '/'
            rel_dirname = os.path.relpath(dirname, start=prefix)
            dir_parts = rel_dirname.split('/')
            if len(dir_parts) == 1:
                dirnames.append(dir_parts[0])
        dirnames = list(set(dirnames))
        if '.' in dirnames:
            dirnames.remove('.')
        return dirnames

    def _create_prefix(self, dirname):
        if dirname in ('.', '/'):
            dirname = ''
        # Strips trailing slash from dir prefix for comparisons
        # os.dirname() returns directory names without a trailing /
        prefix = os.path.join(self._bucket_root, dirname)
        if prefix.endswith('/'):
            prefix = prefix.rstrip('/')
        return prefix

    def delete_file(self, filename):
        """Delete a file from the bucket.

        Parameters
        ----------
        filename : str
            Name of the file, relative to ``bucket_root/``.
        """
        key = os.path.join(self._bucket_root, filename)
        objects = list(self._bucket.objects.filter(Prefix=key))
        for obj in objects:
            obj.delete()

    def delete_directory(self, dirname):
        """Delete a directory (and contents) from the bucket.

        Parameters
        ----------
        dirname : str
            Name of the directory, relative to ``bucket_root/``.
        """
        key = os.path.join(self._bucket_root, dirname)
        if not key.endswith('/'):
            key += '/'

        delete_keys = {'Objects': []}
        key_objects = [{'Key': obj.key}
                       for obj in self._bucket.objects.filter(Prefix=key)]
        assert len(key_objects) > 0
        delete_keys['Objects'] = key_objects
        # based on http://stackoverflow.com/a/34888103
        s3 = self._session.resource('s3')
        r = s3.meta.client.delete_objects(Bucket=self._bucket.name,
                                          Delete=delete_keys)
        log.debug(r)
        if 'Errors' in r:
            raise S3Error('S3 could not delete {0}'.format(key))


class S3Error(Exception):
    """General errors in S3 API usage."""
    pass
