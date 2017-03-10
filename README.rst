.. image:: https://img.shields.io/pypi/v/ltd-mason.svg
.. image:: https://img.shields.io/travis/lsst-sqre/ltd-mason.svg

####################
LSST the Docs: Mason
####################

**Mason** is the build tool for LSST software documentation.
It's flexible and can run as part of a `Travis CI build <https://ltd-mason.lsst.io/travis.html>`_ to upload built documentation to Amazon S3 in coordination with `LTD Keeper <https://ltd-keeper.lsst.io>`_.
Mason can also build documentation for complex multi-repository software projects like the LSST Science Pipelines.

Mason a part of the **LSST the Docs** (LTD) service for continuous documentation delivery.
You can learn more about LTD in our `SQR-006 <http://sqr-006.lsst.io>`_ technote.

Installation
============

Mason is compatible with Python 2.7 and 3.4+.
You can get the latest release from PyPI:

::

   pip install ltd-mason

Docs
====

**Read the docs at https://ltd-mason.lsst.io**

This documentation describes how to use LTD Mason in Travis-based (single repo) and Jenkins-based (multi repo) documentation builds.

****

Copyright 2016-2017 Association of Universities for Research in Astronomy, Inc.

License: MIT.

.. _SQR-006: http://sqr-006.lsst.io
.. _lsstsw: https://github.com/lsst/lsstsw
