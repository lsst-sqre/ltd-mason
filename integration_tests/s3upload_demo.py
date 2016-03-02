#!/usr/bin/env python
"""Demonstration script for ltdmason.s3upload.

This script requires that you have AWS credentials installed according to
http://boto3.readthedocs.org/en/latest/guide/quickstart.html#configuration
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()

import os
import shutil
from tempfile import TemporaryDirectory
from argparse import ArgumentParser
import logging

import boto3
from ltdmason import s3upload

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.ERROR)

    logging.getLogger('ltdmason.s3upload').level = logging.INFO
    logging.getLogger(__name__).level = logging.INFO

    parser = ArgumentParser()
    parser.add_argument('bucketname')
    args = parser.parse_args()

    paths = [
        'file1.txt',
        'file2.txt',
        'dir1/file11.txt',
        'dir1/file12.txt',
        'dir1/dir11/file111.txt',
        'dir1/dir11/file112.txt',
        'dir2/file21.txt',
        'dir2/file22.txt',
    ]

    # with TemporaryDirectory() as temp_dir:
    #    pass  # for python 3 only
    temp_dir = tempfile.mkdtemp()

    create_test_files(temp_dir, paths)

    s3upload.upload(args.bucketname, 'aws/demo', temp_dir)
    test_objects_exist(args.bucketname, 'aws/demo', paths)

    shutil.rmtree(os.path.join(temp_dir, 'dir1'))
    paths.remove('dir1/file11.txt')
    paths.remove('dir1/file12.txt')
    paths.remove('dir1/dir11/file111.txt')
    paths.remove('dir1/dir11/file112.txt')
    os.remove(os.path.join(temp_dir, 'file2.txt'))
    paths.remove('file2.txt')

    s3upload.upload(args.bucketname, 'aws/demo', temp_dir)
    test_objects_exist(args.bucketname, 'aws/demo', paths)

    shutil.rmtree(temp_dir)


def create_test_files(temp_dir, file_list):
    for path in file_list:
        write_file(temp_dir, path)


def write_file(root_dir, rel_path):
    filepath = os.path.join(root_dir, rel_path)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w') as f:
        f.write('Content of {0}'.format(os.path.basename(filepath)))


def test_objects_exist(bucket_name, bucket_root, file_list):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    bucket_objects = []
    for obj in bucket.objects.filter(Prefix=bucket_root):
        if obj.key.endswith('/'):
            continue
        bucket_objects.append(obj.key)

    assert len(bucket_objects) == len(file_list)
    for path in file_list:
        found = False
        for bucket_path in bucket_objects:
            if bucket_path.endswith(path):
                found = True
                continue
        if not found:
            log.error('{0} not found in bucket'.format(bucket_path))
            assert False


if __name__ == '__main__':
    main()
