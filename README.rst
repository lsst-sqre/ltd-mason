.. image:: https://img.shields.io/travis/lsst-sqre/ltd-mason.svg

####################
LSST the Docs: Mason
####################

**Mason** is the build tool for LSST software documentation that runs in the Jenkins build environment.
It is a part of the **LSST the Docs** (LTD) service for continuous documentation deployment.
You can learn more about LTD in our `SQR-006`_ technote.

Installation
============

Mason is intended to work with either Python 2.7, 3.4, or 3.5.

We recommend that you install Mason inside a `virtual environment <https://packaging.python.org/en/latest/installing/#creating-virtual-environments>`_ (such as `virtualenv <https://packaging.python.org/en/latest/projects/#virtualenv>`_ / `virtualenvwrapper <http://virtualenvwrapper.readthedocs.org>`_ on Python 2.7/3 or the built-in `pyenv <http://docs.python.org/3.4/library/venv.html>`_ for Python 3).

If the Sphinx project being built uses Python introspection to build an API reference with `autodoc <http://www.sphinx-doc.org/en/stable/ext/autodoc.html>`_ or `numpydoc <https://pypi.python.org/pypi/numpydoc>`_, then the Python package being documented must be installed in the same virtual environment as Mason.

Install for production
----------------------

Mason is available on PyPI:

::

   pip install ltd-mason

Next, see the `Usage`_ section.

Install for development/testing
-------------------------------

Once the environment is ready, install Mason from this Git repository via:

::

   git clone https://github.com/lsst-sqre/ltd-mason.git
   pip install -r requirements.txt
   python setup.py develop

See `Testing`_ for information on running unit tests.

Usage
=====

Mason is intended to be used as a command line app, ``ltd-mason``.
typical usage is::

   ltd-mason --manifest manifest.yaml

See ``ltd-mason -h`` for additional options.

YAML Manifest
-------------

A YAML-encoded manifest file tells ``ltd-mason`` what documentation to build, and where to find individual packages for multi-package LSST Stack-type build.
The manifest's schema is described in `SQR-006`_, and examples are also available here in the ``tests/`` and ``integration_tests/`` directories.
Formally the manifest schema is defined in `manifest_schema.yaml`_.

.. _manifest_schema.yaml: ./manifest_schema.yaml

Enviroment Variables and AWS credentials
----------------------------------------

LTD Mason is configured through environment variables.

Credentials for AWS S3
^^^^^^^^^^^^^^^^^^^^^^

``LTD_MASON_AWS_ID``
   AWS access key ID.

``LTD_MASON_AWS_SECRET``
   AWS secret access key.

``LTD_MASON_AWS_PROFILE``
   This variable can be set as an alternative ``LTD_MASON_AWS_ID`` and ``LTD_MASON_AWS_SECRET``. ``LTD_MASON_AWS_PROFILE`` is the name of a profile in `~/.aws/credentials` that contains your secret key and ID. See the `boto3 configuration guide <http://bit.ly/1WuF7rY>`_ for more information.

If None of these variables are configured, LTD Mason will attempt to use the `default AWS credential setup <http://bit.ly/1WuF7rY>`_ in your environment.

Note that the AWS credentials specified here must have permission to read and write into the S3 buckets managed by the LTD Keeper server.

Credentials for LTD Keeper
^^^^^^^^^^^^^^^^^^^^^^^^^^

``LTD_KEEPER_URL``
   URL of LTD Keeper instance.

``LTD_KEEPER_USER``
   Username for LTD Keeper instance.

``LTD_KEEPER_PASSWORD``
   Password for LTD Keeper instance.

Testing
=======

Unit and integration tests are available.

Unit tests
----------

Developers can run unit tests via `pytest <http://pytest.org>`_::

   py.test

To run a full suite of AWS S3 integration tests, you'll need AWS credentials and an S3 bucket to test in.
Configure the tests to use these by setting the following environment variables:

``LTD_MASON_TEST_AWS_ID``
   AWS access key ID

``LTD_MASON_TEST_AWS_SECRET``
   AWS secret access key

``LTD_MASON_TEST_BUCKET``
   Name of an S3 bucket that already exists and can be used for testing.

Integration tests
-----------------

We have separate integration tests to exercise code that interacts with AWS S3 and ltd-keeper.
See ``integration_tests/README.rst`` for instructions on how to run these integration tests.

Release Procedures
==================

LTD Mason is distributed with PyPI at https://pypi.python.org/pypi/ltd-mason/.
Follow this procedure to create a new release:

1. Ensure the version in ``setup.py`` is correct. Use ``x.y.z.devN`` for development versions.

2. Test the metadata::

      python setup.py check --metadata --restructuredtext --strict

3. Build the distributions::
   
      rm -R dist
      python setup.py sdist bdist_wheel

4. Upload the distributions with `twine <https://pypi.python.org/pypi/twine>`_::

      twine upload dist/*

****

Copyright 2016 AURA/LSST.

License: MIT.

.. _SQR-006: http://sqr-006.lsst.io
.. _lsstsw: https://github.com/lsst/lsstsw
