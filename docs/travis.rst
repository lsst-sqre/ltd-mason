###########################
Running LTD Mason on Travis
###########################

If your project already uses `Travis CI`_ for continuous integration, you may want to run LTD Mason there for documentation deployment as well.
Projects well suited for Travis-based Mason deployments are:

- Pure-Sphinx projects such as `Technotes <http://sqr-000.lsst.io>`_ and the `DM Developer Guide <https://developer.lsst.io>`_.
- Python package documentation.

Documentation for EUPS-based packages need to be run from a Jenkins-based CI environment.
See :doc:`jenkins`.

Composing .travis.yml for LSST the Docs
=======================================

Projects need to include a :file:`.travis.yml` file in their root to activate `Travis CI`_.
You can read more about :file:`.travis.yml` from the `Travis documenation <https://docs.travis-ci.com/user/customizing-the-build>`_.

The exact construction of this file depends on how you need to use Travis to run tests for your project, or if you are only building documentation.
This guide will outline how to deploy documentation in both cases.

When crafting :file:`.travis.yml`, we recommend using `Travis' validator <https://docs.travis-ci.com/user/travis-lint>`_, available online or through the ``travis`` command line app.

Environment variables and secrets
---------------------------------

Regardless of context, all projects using Travis to deploy to LSST the Docs need to configure the Travis CI build environment through environment variables.
This is a sample ``env`` section:

.. code-block:: yaml

   env:
     global:
       - LTD_MASON_BUILD=false  # disable builds in regular text matrix
       - LTD_MASON_PRODUCT="sims-operations"
       - LTD_KEEPER_URL="https://keeper.lsst.codes"
       # travis encrypt "LTD_MASON_AWS_ID=... LTD_MASON_AWS_SECRET=..."
       - secure: "K332NczWP7D7qczaqXmcFq1nNT6/PeZ14rtRK0sFDo7/7u6KwLvhe5biXOgmKJmoOFlXoBg93uRn3tewRKvVpffPzrWwOlOHMNPR90X6uOubFxnd/IXFSWXOtEoKguKv71kTJANJvjhJkEtKm0cjrfAIBo8hMiiOqR9782oB/FQ="
       # travis encrypt "LTD_KEEPER_USER=... LTD_KEEPER_PASSWORD=..."
       - secure: "B3bdOBOnrhb+YFaFKG0LDZ5ETGb8MnH3VdmkmrM9BNmcO9X8q39gqI9cXVaOFrqLHCBkAtLZus5pGeEetxG/87gAE04JDPWjSMCkMyszUMn8fpv3WgRGxmhKxNAlHHVFOiRJLaE2j58YnQtcXYLyIeGWe3QH6Zk+LHHaOJqtqeU="

By including these environment variables under ``env.global`` we ensure that the entire set is applied to all builds; including environment variables directly in ``env`` creates a build matrix.

``LTD_MASON_BUILD=false`` should always be present to ensure that LTD Mason is *only* run on the build you specify, rather than all entries of a Travis build matrix.

``LTD_MASON_PRODUCT`` should be set to the project's slug (specified when the project was created on LTD Keeper).

``LTD_KEEPER_URL`` is the URL of the Keeper API server. For LSST the Docs this is ``https://keeper.lsst.codes``.

The next two lines contain `encrypted environment variable <https://docs.travis-ci.com/user/environment-variables/#Encrypted-Variables>`_ settings for ``LTD_KEEPER_USER``/``LTD_KEEPER_PASSWORD`` (credentials for Travis to work with LTD Keeper) and ``LTD_MASON_AWS_ID``/``LTD_MASON_AWS_SECRET`` (credentials for Travis to upload to AWS S3).

Encrypting variables requires the Travis gem, which can be installed with:

.. code-block:: bash

   gem install travis

From the **root of your Git repository**, encrypt the environment variables using

.. code-block:: bash

   travis encrypt "LTD_MASON_AWS_ID=... LTD_MASON_AWS_SECRET=..."
   travis encrypt "LTD_KEEPER_USER=... LTD_KEEPER_PASSWORD=..."

Paste the results as list items into the ``env.global`` section of :file:`.travis.yml`.

Alternatively you could pass the ``--add env.global`` flag to ``travis encrypt``, but note that your *entire* :file:`.travis.yml` file will be reformatted.

These settings can be securely checked into GitHub since only Travis possesses the private key needed to decrypt those ``secure`` lines.

You may need to ask an LSST the Docs administrator to add these encrypted lines since the Keeper and AWS credentials are not widely distributed.

Travis setup for a pure Sphinx repository
-----------------------------------------

The sample :file:`travis.yml` file below shows how Travis can be configured to build a pure-documentation repository (such as a `Technote <http://sqr-000.lsst.io>`_).

.. code-block:: yaml
   :linenos:

   sudo: false
   language: python
   matrix:
     include:
       # This is the ltd-mason documentation deployment build
       - python: "3.5"
         env: LTD_MASON_BUILD=true
   install:
     - pip install -r requirements.txt
     - pip install ltd-mason
   script:
     - sphinx-build -b html -a -n -W -d _build/doctree . _build/html
   after_success:
     - ltd-mason-travis --html-dir _build/html
   env:
     global:
       - LTD_MASON_BUILD=false  # disable builds in regular text matrix
       - LTD_MASON_PRODUCT="dmtn-013"
       # travis encrypt "LTD_MASON_AWS_ID=... LTD_MASON_AWS_SECRET=... LTD_KEEPER_URL=... LTD_KEEPER_USER=... LTD_KEEPER_PASSWORD=..." --add env.global 
       - secure: "edPD6RMPjPCvuuqtXc3nmQ2T5tvVWWFnhC957tmqyzvFS++cEZLXRCRRenlxd+9ygm7qONWXtcvJeyWiaVi9pooeFpIKlcVWeJQAZD+oLsONrFBzdPQrP8ObaeD845T9meFR+k48uFpvB2yHc3e0ZUczhxJbKUxSQzlX1xRIVh9YwwWCLbBitNHcTNsnNDfdvxFw5w3CTkWdd8j6962eOzOQHgO/Ta5B71Ab/0XwVWEh7C5mE3jNq4GRLlEXp9vyDr0DzHihVN/XkMMeSTrUj20pHePvxJh0lJi6zmseX5RCKu1hVe7dvv2FUySVB/BzW6O4kFgS7L3ynaF5jGhiIjkGMwIgd+o1ucDbuPtFqk6e1SBGwc2y2ZVijN/D2ZeQOWGDx2lUrVbdmP3MW5YQDuHfep/8H0npmvd/pUlnIjT/cxSMVW0rQlH0O+ZyTbR30lX1JRCzHgjDqX78m1JHaaOdAjcJ+3GfLRr7vWaCr4mb9NbKMCgtkt6efN6E/cfTB8xbFC0x/TF2QcKIWGQKWxCnGuXgqXlOsoR367kgqWps5l5jGmndth24/sK0UWBlqE9Vkhi3ea58Uprh6RjlMvG/6syAhhsDR1u+T48T3ABpKJHhkrbRncxpiWyki3s9t8z85MLD2dBqPF8RanaeI/86ecoNln1imcWRViCwyFQ="

In this Travis configuration, the Sphinx documentation repository's dependencies specified in a :file:`requirements.txt` are installed, along with ``ltd-mason``.

In the ``script`` stage we build the Sphinx project with ``sphinx-build``.
The flags and options are as follows:

- ``-b html`` to build HTML.
- ``-a`` to force a complete build. This should be an issue on Travis, but including the flag does protect against cases where the HTML build output was accidentally checked into the Git repository.
- ``-n -W`` activates 'nitpicky mode' where broken references become warnings, and warnings are elevated to errors that cause ``sphinx-build`` to exit ``1`` and fail the build.
- ``.`` is the root directory of the documentation relative to the root of the Git repository; here the Sphinx project resides at the root of the Git repository.
- ``_build/html`` specifies an output directory for the built HTML.

**Note:** Unlike the ``ltd-mason`` build tool, ``ltd-mason-travis`` defers the Sphinx build step to the Travis environment (Travis excels at executing and logging scripts already).

If the Sphinx build was successful, the ``after_success`` stage is executed.
Here we run ``ltd-mason-travis`` to deploy the built documentation.
The HTML output directory from ``sphinx-build`` must match the ``--html-dir`` argument for ``ltd-mason-travis``.

Note that we use ``matrix.include`` to include a single Travis build.
This technique is for forwards compatibility if continuous integration testing against multiple environments is later added to a project---such as the next example.

Travis setup for LSST the Docs deployment alongside Python CI
-------------------------------------------------------------

In many cases you will want to use Travis for continuous integration of a software package, in addition to documentation deployment.
The following :file:`travis.yml` sample shows how this can be achieved.

.. code-block:: yaml
   :linenos:
   :emphasize-lines: 11-14,19-23

   sudo: false
   language: python
   python:
     - '2.7'
     - '3.4'
     - '3.5'
     - '3.5-dev'
   matrix:
     allow_failures:
       - python: "3.5-dev"
     include:
       # This is the ltd-mason documentation deployment build
       - python: "3.5"
         env: LTD_MASON_BUILD=true
   install:
     - pip install -r requirements.txt
     - pip install ltd-mason
     - pip install -e .
   script:
     - py.test --flake8 --cov=ltdmason
     - sphinx-build -b html -a -n -W -d docs/_build/doctree docs docs/_build/html
   after_success:
     - ltd-mason-travis --html-dir docs/_build/html
   env:
     global:
       - LTD_MASON_BUILD=false  # disable builds in regular text matrix
       - LTD_MASON_PRODUCT="ltd-mason"
       # travis encrypt "LTD_MASON_AWS_ID=... LTD_MASON_AWS_SECRET=... LTD_KEEPER_URL=... LTD_KEEPER_USER=... LTD_KEEPER_PASSWORD=..." --add env.global 
       - secure: "CIpaoNzWwEQngjmj0/OQBRUOnkT9Rq8273N5ZgXmZTtVSliukfJMROQnp9m42x3a2XFamaYV60mmuAvMRNU8VHi4nePxF2vp7utVnp8cF4zFQQzL6KnN2rqWv0H3Snqc1sfMT2n4H9qgBlYG7w5Cv52VIXdwh8MqGSxl8HAiYgqcVNJ+q1Rxeb1Yk+Bv3VW6O0/K4AlrhGY2Gl/zbwgM4ph0K0UvT1IZg8ZjCdddOpgwxPq66kvzHNcpCR6JUnvy5vRVH+IgC83Ar+oJqOA/4pizcFccriLF7nANkVJMrRSL8B1h2IHuuGYpC2VzDPMlAuEPmU6t8QAhVCOq9BSy98902TgKkvt4enPcxS2iNqMoOJSNUW7q9yqvVacz4JApJfHWlq5K7uTy00p4XHV4TUs+9NEgBUCwEFE5CXcRQvg+Y2y1wqUUkH+12nb1Nv4CdGxG6k7yG+eM+qmANJ87jZK9vX0RmDLKXuA3gpJyVomrAKX1+MqqwD0Qu885AUsHCQevO+oDmXv6nKLK/x2ZeyHQrgWISj3LXU6B7LarLrqsrE7JWTwgo/iX6xiVHS422tj94/+rab3JarBWe+ntdG9rZBdILU92kLqzgMA570ryVxtsnu8GnzOB0/3yvdtW+duAgrrBUusBcg9E/Kz/68Cm5RbMLyjaeA6HxP6mfM4="

Here, the ``python`` section defines a matrix of builds against several versions of Python.
During each build, the lines specified in the ``install`` section are executed, followed by the 
``script`` section.

The ``install`` stage first installs the Python project's development dependencies specified in :file:`requirements.txt`, followed by the ``ltd-mason`` package and the Python package itself.

In the ``script`` stage we run tests (``py.test``, in this example) and then ``sphinx-build``.
Again, we have configured Sphinx to fail the build on any warnings so you effectively get CI of the documentation in addition to code.

Finally, in the ``after_success`` stage we trigger ``ltd-mason-travis`` to deploy the previously-built HTML resources.
For Travis projects that CI code we want ``ltd-mason-travis`` to run in the ``after_success`` stage to ensure that documentation is only deployed for commits that don't have issues.

Notice that each environment in the build matrix (Python 2.7, 3.4, and so on)  executes ``ltd-mason-travis``.
However, we only want a single documentation deployment from each code push.
We solve this by setting the default value of ``LTD_MASON_BUILD`` to ``false``, which causes ``ltd-mason-build`` to skip deployment.
It's only in the extra build environment specified in ``matrix.include`` that we change ``LTD_MASON_BUILD`` to ``true``.
This technique allows you to create a build matrix for CI without worrying about multiple accidental documentation deployments.


.. _Travis CI: https://travis-ci.org
