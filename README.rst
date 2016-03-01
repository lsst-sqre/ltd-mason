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

Installing for development/testing
----------------------------------

Once the environment is ready, install Mason from this Git repository via:

::

   pip install -r requirements.txt
   python setup.py develop

See :ref:`Testing` for information on testing.

Usage
=====

Mason is intended to be used as a command line app, ``ltd-mason``.
A YAML-encoded manifest file tells ``ltd-mason`` what documentation to built, and where to find individual LSST Stack packages built by lsstsw_.
The manifest's schema is described in `SQR-006`_, and examples are also available here in the :file:`tests/` and :file:`integration_tests/` directories.

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
See :file:`integration_tests/README.rst` for instructions on how to run these integration tests.

****

Copyright 2016 AURA/LSST.

License: MIT.

.. _SQR-006: http://sqr-006.lsst.io
.. _lsstsw: https://github.com/lsst/lsstsw
