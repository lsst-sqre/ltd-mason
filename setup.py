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
        'Programming Language :: Python :: 3',
    ],
    keywords='lsst',
    packages=find_packages(exclude=['docs', 'tests*', 'data']),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=['ruamel.yaml',
                      'sh',
                      'boto3',
                      'jsonschema',
                      'requests'],
    # package_data={},
    entry_points={
        'console_scripts': [
            'ltd-mason = ltdmason.cli:run_ltd_mason',
            'ltd-mason-travis = ltdmason.traviscli:run',
            'ltd-mason-make-redirects = ltdmason.redirectdircli:run',
        ]
    }
)
