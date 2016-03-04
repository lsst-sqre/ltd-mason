#################
Integration Tests
#################

In addition to unit tests, with py.test, we use integration tests to validate the end-to-end functionality of ltd-mason.
This document describes how to set up and run these tests.

One integration test is currently available:

1. :ref:`run-ltd-mason.sh` – End-to-end Testing

run-ltd-mason.sh – End-to-end Testing
=====================================

Prerequisites
-------------

lsstsw Stack
^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/lsst/lsstsw.git
   cd lsstsw
   ./bin/deploy
   . bin/setup.sh
   rebuild lsst_apps
   eups tags --clone bNNNN current

Then get a version of ``afw`` that has Sphinx documentation enabled:

.. code-block:: bash

   cd lsstsw/build/afw
   git fetch
   git checkout u/jonathansick/DM-4195
   eups declare -r . -t $USER afw git
   setup afw git
   scons doc

Finally, set the environment variable :envvar:`STACK_AFW` to the directory where the build ``afw`` is located in :file:`lsstsw/stack`.

AWS Credentials
^^^^^^^^^^^^^^^

Add AWS credentials to the default profile (specifically, ones for lsst-sqre's account) to :file:`~/.aws/credentials`.
See http://boto3.readthedocs.org/en/latest/guide/quickstart.html#configuration.

Install ltd-mason
^^^^^^^^^^^^^^^^^

ltd-mason should be installed with the same Python as the lsstsw-based stack.

.. code-block:: bash

   pip install -r requirements.txt
   python setup.py develop

Start ltd-keeper in development mode
------------------------------------

Install `ltd-keeper <https://github.com/lsst-sqre/ltd-keeper>`_.
Note you'll need to install ltd-keeper in a Python 3.5 environment, which will probably be different from the Python environment used by lsstsw.

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

The :command:`run-ltd-mason.sh` script runs ltd-mason using the :file:`config.yaml` and :file:`manifest.yaml` configuration files provided alongside it.

You should see the documentation be built, published to ltd-keeper, and uploaded to the ``lsst-the-docs-test`` bucket.
