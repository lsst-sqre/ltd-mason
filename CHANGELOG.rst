##########
Change Log
##########

[0.2.4] - 2017-06-05
====================

Changed
-------

- Pin ruamel.yaml to versions >=0.10,<0.15.
  This protects against an API change in 0.15. (See PR #44).
- Pin botocore to 1.5.24 and boto3 to 1.4.4.
  We're seeing an issue with botocore 1.5.60 under Python 2.7.
- Use versioneer for package versioning based on Git tags.

[0.2.3] - 2017-03-13
====================

Changed
-------

- Make ACL-less uploads the default.
  We now expect the *bucket* to have a public-read ACL.
  This makes it easier to create lightweight IAM users that can handle uploads for individual projects.

[0.2.2] - 2016-07-28
====================

Added
-----

- LTD Mason creates and uploads directory redirect objects to S3.
  With Fastly/Varnish, these enable courtesy redirects like ``example.com/dir`` to ``example.com/dir/index.html``.
- A new ``ltd-mason-make-directs`` CLI backfills such objects into an existing S3 bucket.

[0.2.0] - 2016-05-05
====================

Added
-----

- ``ltd-mason-travis`` is an alternate version of the ``ltd-mason`` command line app intended to run from a Travis CI environment for non-Eups project documentation. ``ltd-mason-travis``  defers the Sphinx build step to the Travis build setup (.travis.yml).
- Documentation for crafting a :file:`.travis.yml`.
- Added a Developer Workflow guide.
- Added the Change Log and License to the documentation.

[0.1.0] - 2016-03-15
====================

Added
-----

- Initial version that includes an ``ltd-mason`` command line tool to build multi-package EUPS documentation project given a metadata.yaml file.
- Defined a schema for metadata.yaml.
