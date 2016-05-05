#########################################
Development, Testing and Release Workflow
#########################################

Developer Installation
======================

First, create an `isolated Python environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_ for this project with virtualenv, virtualenvwrapper or pyvenv.
You can develop in Python 2.7 or Python 3.4+.

Then install LTD Mason and its dependencies with:

.. code-block:: bash

   git clone https://git.com/lsst-sqre/ltd-mason.git  # or a fork
   cd ltd-mason
   pip install -r requirements.txt
   python setup.py develop

Testing Framework
=================

Tests are written for, and run through, py.test.

.. code-block:: bash

   py.test --flake8 --cov=ltdmason

Performs unit tests, runs Flake8, and produces a unit test coverage report.

These tests are also run under Travis CI.
On Travis some additional integration tests against AWS S3 are also run.

Coding Style
============

This project follows `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_.

Python Version Compatibility
============================

This project is targeted for both Python 2.7 and Python 3.4+ version.
We use the `future` package to achieve compatibility.

Generally speaking, you should write code for Python 3 and then achieve backwards compatibility by including the following imports:

.. code-block:: py

   from __future__ import (division, absolute_import, print_function,
                           unicode_literals)
   from builtins import *  # NOQA
   from future.standard_library import install_aliases
   install_aliases()  # NOQA

Release Procedure
=================

Ensure that the build is passing on Travis before preparing a release.

1. Bump the version in :file:`setup.py`, update the CHANGELOG (see http://keepachangelog.com) and commit the change.

   For version numbering, see `PEP 386 <https://www.python.org/dev/peps/pep-0386/#the-new-versioning-algorithm>`_.
   E.g.

   - ``0.1.0rc0``
   - ``0.1.0.dev0``

2. Tag:

   .. code-block:: bash

      git tag -s -m "Verson 0.1.0rc0" v0.1.0rc0

3. Build:

   .. code-block:: bash
      
      rm -R dist
      python setup.py sdist bdist_wheel

4. Upload:

   .. code-block:: bash

      twine upload dist/*
      git push --tags
