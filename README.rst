####################
LSST the Docs: Mason
####################

**Mason** is the build tool for LSST software documentation that runs in the Jenkins build environment.
It is a part of the **LSST the Docs** (LTD) service for continuous documentation deployment.
You can learn more about LTD in our `SQR-006`_ technote.

Installation
============

Mason is intended to work with either Python 2.7, 3.4, or 3.5.
It *must* run from the same Python as the software being documented, however.

::

   pip install -r requirements.txt
   python setup.py install

Usage
=====

Mason is intended to be used as a command line app, ``ltd-mason``.
A YAML-encoded manifest file tells ``ltd-mason`` what documentation to built, and where to find individual LSST Stack packages built by lsstsw_.
The manifest's schema is described in `SQR-006`_, and examples are also available here in the :file:`tests/` directory.

Typical usage is::

   ltd-mason --manifest manifest.yaml

Run ``ltd-mason --help`` for more information.

Testing
=======

Unit and integration tests are available.

Unit tests
----------

Developers can run unit tests via `pytest <http://pytest.org>`_::

   py.test

To run the full set of tests, the :envvar:`STACK_AFW` environment variable should be set to the path of the installed ``afw`` package in the ``lsstsw/stack`` directory.
Some tests will be skipped if :envvar:`STACK_AFW` is not set.

Integration tests
-----------------

We have separate integration tests to exercise code that interacts with AWS S3 and ltd-keeper.
See :file:`integration_tests/README.rst`.

****

Copyright 2016 AURA/LSST.

License: MIT.

.. _SQR-006: http://sqr-006.lsst.io
.. _lsstsw: https://github.com/lsst/lsstsw
