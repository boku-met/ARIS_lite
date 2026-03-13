Installation Guide
===================

Overview
--------

To install ARIS-lite, you currently can use pip or uv. The package has
been tested with Python 3.13.

Installation
------------

*Using uv (recommended)*:

Set up a project directory, open a terminal, and do

.. code-block:: shell

   uv venv
   source .venv/bin/activate
   uv pip install git+https://github.com/j-haacker/aris_lite.git

Advantages:

- Does not rely on the system Python.
- Does not stuff your system.
- It is fast.

*Using pip (alternative)*:

.. code-block:: shell

   pip install git+https://github.com/j-haacker/aris_lite.git

Dependencies
-------------

ARIS-lite requires the following packages:

- ``dask[complete]``
- ``numpy``
- ``pandas``
- ``snowmaus``
- ``xarray[accel,io,parallel]``
- ``zarr>=3``

These dependencies will be automatically installed when you use one of
the above.

Troubleshooting
---------------

If you encounter any issues during installation or while using
ARIS-lite, please check the project's GitHub repository for known issues
and solutions.

Next Steps
---------

Once installed, you can proceed to the usage documentation to learn how
to use ARIS-lite in your projects:

.. toctree::
   :maxdepth: 1

   usage
