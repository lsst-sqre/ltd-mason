from setuptools import setup, find_packages
import os
from io import open
import versioneer


packagename = 'ltd-mason'
description = 'LSST the Docs build tool'
author = 'Jonathan Sick'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/ltd-mason'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return open(full_filename, mode='r', encoding='utf-8').read()


long_description = read('README.rst')


setup(
    name=packagename,
    version=versioneer.get_version(),
    description=description,
    long_description=long_description,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='lsst',
    packages=find_packages(exclude=['docs', 'tests*', 'data']),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=['future>=0.15',
                      'ruamel.yaml>=0.10,<0.15',
                      'sh>=1.11',
                      # botocore 1.5.60 is known ot have python 2.7 issues
                      # This temporarily freezes to a working release.
                      'boto3==1.4.4',
                      'botocore==1.5.24',
                      'jsonschema>=2.5',
                      'sphinx>=1.4',
                      'requests>=2.9'],
    # package_data={},
    entry_points={
        'console_scripts': [
            'ltd-mason = ltdmason.cli:run_ltd_mason',
            'ltd-mason-travis = ltdmason.traviscli:run',
            'ltd-mason-make-redirects = ltdmason.redirectdircli:run',
        ]
    }
)
