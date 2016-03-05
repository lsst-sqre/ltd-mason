#################
Integration Tests
#################

In addition to unit tests, with py.test, we use integration tests to validate the end-to-end functionality of ltd-mason.
This document describes how to set up and run these tests.

One integration test is currently available:

1. `run-ltd-mason`_ – End-to-end Testing

.. _run-ltd-mason:

run-ltd-mason.sh – End-to-end Testing
=====================================

Prerequisites
-------------

1. Install LTD Mason for development by cloning it and installing in development mode (``python setup.py develop``); see the project README.
2. Configure AWS credentials per the project README; the integration test assumes SQuaRE's account.
3. Configure LTD Keeper environment variables, per the project README::

      export LTD_KEEPER_URL=http://localhost:5000
      export LTD_KEEPER_USER=user
      export LTD_KEEPER_PASSWORD=pass


Start LTD Keeper in development mode
------------------------------------

Install `LTD Keeper <https://github.com/lsst-sqre/ltd-keeper>`_.
Note you'll need to install ltd-keeper in a Python 3.5 environment, which *can* be different from the Python environment that LTD Mason runs in.

Start up the ltd-keeper server:

.. code-block:: bash

   ./run.py

Then initialize a test product using the :file:`/ltd-mason/integration_tests/setup_keeper.yaml`.

.. code-block:: bash

   cd ltd-mason/integration_tests
   ./setup_keeper.py

Note that this can only be done once; to re-run the integration test you'll need to shut down the ltd-keeper server, delete the development sqlite DB, restart ltd-keeper and re-run :command:`setup_keeper.py`.

Run the integration test
------------------------

The :command:`run-ltd-mason.sh` script runs ``ltd-mason`` using the ``mock_manifest.yaml`` configuration file provided in the ``tests/`` directory.

You should see the documentation be built, published to LTD Keeper, and uploaded to the ``lsst-the-docs-test`` bucket.
