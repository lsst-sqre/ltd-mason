"""S3 upload/sync utilities."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()

import os

import boto3


def upload(bucket_name, path_prefix, source_dir):
    """Upload built documentation to S3.

    This function places the contents of the Sphinx HTML build directory
    into the ``/path_prefix/`` directory of an *existing* S3 bucket.
    Existing files on S3 are overwritten; files that no longer exist in the
    ``source_dir`` are deleted from S3.

    S3 credentials are assumed to be stored in a place where boto3 can read
    them, such as :file:`~/.aws/credentials`.
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
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    manager = ObjectManager(bucket, path_prefix)

    for (rootdir, dirnames, filenames) in os.walk(source_dir):
        print('Local directory: {0}'.format(rootdir))
        # name of root directory on S3 bucket
        bucket_root = os.path.relpath(rootdir, start=source_dir)
        if bucket_root in ('.', '/'):
            bucket_root = ''

        # Delete bucket directories that no longer exist in source
        bucket_dirnames = manager.list_dirnames_in_directory(bucket_root)
        for bucket_dirname in bucket_dirnames:
            if bucket_dirname not in dirnames:
                manager.delete_directory(bucket_dirname)

        # Delete files that no longer exist in source
        bucket_filenames = manager.list_filenames_in_directory(bucket_root)
        for bucket_filename in bucket_filenames:
            if bucket_filename not in filenames:
                bucket_filename = os.path.join(bucket_root, bucket_filename)
                manager.delete_file(bucket_filename)

        # Upload files in directory
        for filename in filenames:
            local_path = os.path.join(rootdir, filename)
            bucket_path = os.path.join(path_prefix, bucket_root, filename)
            _upload_file(local_path, bucket_path, bucket)


def _upload_file(local_path, bucket_path, bucket):
    """Upload a file to the S3 bucket.

    Parameters
    ----------
    local_path : str
        Full path to a file on the local file system.
    bucket_path : str
        Destination path (also known as the key name) of the file in the
        S3 bucket.
    bucket : `boto3` Bucket instance
        S3 bucket.
    """
    obj = bucket.Object(bucket_path)
    # no return status from the upload_file api
    obj.upload_file(local_path)


class ObjectManager(object):
    """Manage objects existing in a bucket under a specific ``bucket_root``.

    The ObjectManager maintains information about objects that exist in the
    bucket, and can delete objects that no longer exist in the source.

    Parameters
    ----------
    bucket : `boto3` Bucket instance
        S3 bucket.
    bucket_root : str
        The version slug is the name root directory in the bucket where
        documentation is stored.
    """
    def __init__(self, bucket, bucket_root):
        super().__init__()
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
            if obj.key.endswith('/'):
                # object is a S3 directory object
                dir_parts = obj.key.rstrip('/').split('/')
                # check that directory is at root of dirname
                base_dir = '/'.join(dir_parts[:-1])
                if base_dir == prefix:
                    dirnames.append(os.path.relpath(obj.key,
                                                    start=prefix))
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
        assert len(objects) == 1
        obj = objects[0]
        r = obj.delete()
        status_code = r['ResponseMetadata']['HTTPStatusCode']
        if status_code >= 300:
            raise S3Error('S3 could not delete {0} (status {1:d})'.format(
                key, status_code))

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
        s3 = boto3.resource('s3')
        r = s3.meta.client.delete_objects(Bucket=self._bucket.name,
                                          Delete=delete_keys)
        status_code = r['ResponseMetadata']['HTTPStatusCode']
        if status_code >= 300:
            raise S3Error('S3 could not delete {0} (status {1:d})'.format(
                key, status_code))


class S3Error(Exception):
    """General errors in S3 API usage."""
    pass
