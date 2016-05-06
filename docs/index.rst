#########
LTD Mason
#########

**Mason** is the build tool for LSST software documentation.
It's flexible and can run as part of a :doc:`Travis CI build <travis>` to upload built documentation to Amazon S3 in coordination with `LTD Keeper <https://ltd-keeper.lsst.io>`_.
Mason can also build documentation for complex multi-repository software projects like the LSST Science Pipelines.

Mason is a part of the **LSST the Docs** (LTD) service for continuous documentation delivery.
You can learn more about LTD in our `SQR-006 <https://sqr-006.lsst.io>`_ technote.

Mason is developed on GitHub at https://github.com/lsst-sqre/ltd-mason.
Releases are `available on PyPI <https://pypi.python.org/pypi/ltd-mason/>`_:

.. code-block:: bash

   pip install ltd-mason

.. toctree::
   :maxdepth: 1
   :caption: User Guide
   :name: part-guide

   travis
   jenkins

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide
   :name: part-dev

   dev-workflow

.. toctree::
   :maxdepth: 1
   :caption: Project Information
   :name: part-info

   license
   changelog
