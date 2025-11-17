Installation Guide
===================

Overview
--------

To install ARIS_lite, you currently can use pip or uv. The package has
been tested with Python 3.13.

Installation
------------

Using uv (recommended):

- set up a project directory, open a terminal, and

.. code-block:: shell

   uv venv
   source .venv/bin/activate
   uv pip install git+https://github.com/j-haacker/ARIS_lite.git

Advantage:

- does not rely on the system Python
- does not stuff your system
- it is fast

Using pip (alternative):

.. code-block:: shell
   
   pip install git+https://github.com/j-haacker/ARIS_lite.git

Dependencies
-------------

ARIS_lite requires the following packages:

- dask[complete]
- numpy
- pandas
- snowmaus
- xarray[accel,io,parallel]
- zarr>=3

These dependencies will be automatically installed when you use one of
the above.

Troubleshooting
---------------

If you encounter any issues during installation or while using
ARIS_lite, please check the project's GitHub repository for known issues
and solutions.

Next Steps
---------

Once installed, you can proceed to the usage documentation to learn how
to use ARIS_lite in your projects:

.. toctree::
   :maxdepth: 1

   usage
