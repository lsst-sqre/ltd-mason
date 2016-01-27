"""S3 upload/sync utilities."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *
from future.standard_library import install_aliases
install_aliases()

import boto3


def upload(bucket_name, version_slug, source_dir):
    """Upload built documentation to S3.

    This function places the contents of the Sphinx HTML build directory
    into the ``/version_slug/`` directory of an *existing* S3 bucket.
    Existing files on S3 are overwritten; files that no longer exist in the
    ``source_dir`` are deleted from S3.

    S3 credentials are assumed to be stored in a place where boto3 can read
    them, such as :file:`~/.aws/credentials`.
    See http://boto3.readthedocs.org/en/latest/guide/quickstart.html.

    Parameters
    ----------
    bucket_name : str
        Name of the S3 bucket where documentation is uploaded.
    version_slug : str
        The version slug is the name root directory in the bucket where
        documentation is stored.
    source_dir : str
        Path of the Sphinx HTML build directory on the local file system.
        The contents of this directory are uploaded into the ``/version_slug/``
        directory of the S3 bucket.
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    manager = ObjectManager(bucket, version_slug)

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
            bucket_path = os.path.join(version_slug, bucket_root, filename)
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
    pass


class ObjectManager(object):
    """Manage objects existing in a bucket under a specific ``version_slug``.

    The ObjectManager maintains information about objects that exist in the
    bucket, and can delete objects that no longer exist in the source.

    Parameters
    ----------
    bucket : `boto3` Bucket instance
        S3 bucket.
    version_slug : str
        The version slug is the name root directory in the bucket where
        documentation is stored.
    """
    def __init__(self, bucket, version_slug):
        super().__init__()
        self._version_slug = version_slug
        if not self._version_slug.endswith('/'):
            self._version_slug = self._version_slug + '/'
        self._objects = self._bucket.objects.filter(Prefix=self._version_slug)

    def list_filenames_in_directory(self, dirname):
        """List all file-type object names that exist at the root of this
        bucket directory.

        Parameters
        ----------
        dirname : str
            Directory name in the bucket relative to ``version_slug/``.

        Returns
        -------
        filenames : list
            List of file names (`str`), relative to ``version_slug/``, that
            exist at the root of ``dirname``.
        """
        return []

    def list_dirnames_in_directory(self, dirname):
        """List all names of directories that exist at the root of this
        bucket directory.

        Note that *directories* don't exist in S3; rather directories are
        inferred from path names.

        Parameters
        ----------
        dirname : str
            Directory name in the bucket relative to ``version_slug``.

        Returns
        -------
        dirnames : list
            List of directory names (`str`), relative to ``version_slug/``,
            that exist at the root of ``dirname``.
        """
        return []

    def delete_file(self, filename):
        """Delete a file from the bucket.

        Parameters
        ----------
        filename : str
            Name of the file, relative to ``version_slug/``.
        """
        pass

    def delete_directory(self, dirname):
        """Delete a directory (and contents) from the bucket.

        Parameters
        ----------
        dirname : str
            Name of the directory, relative to ``version_slug/``.
        """
        pass
