Usage Guide
============

Overview
--------

This guide explains how to use the ARIS_lite package to compute plant
stress indicators from modelling the soil water balance using
meteorological data.

Main Components
---------------

ARIS_lite consists of the following modules:

- ``water_budget.py``: Handles soil water balance calculations
- ``phenology.py``: Implements phenological models
- ``yield_expectation.py``: Calculates crop yield expectations

Basic Usage
-----------

To use ARIS_lite, you can either:

1. Use the command-line interfaces (CLIs) provided by the package
2. Import and use the functions programmatically

In any case, first make sure your data is organized in Zarr stores with
the correct variable names and with the correct units. The list below
may be incomplete - in that case, refer to the source code. If not
specified, the variables correspond to daily aggregates at 2 m above the
surface, with temperatures in ˚C.

- ``air-temperature``: Average air temperature
- ``max-air-temp``: Maximum air temperature
- ``min-air-temp``: Maximum air temperature
- ``rel_humidity``: Average relative humidity in %
- ``min_rel_hum``: Minimum relative humidity in %
- ``precipitation``: Total precipitation in mm water equivalent
- ``wind_speed``: Wind speed in m/s 10 m above the surface
- ``pot_evapotransp``: Average potential evapotranspiration in mm water equivalent

Command-Line Usage
------------------

The ``aris-1go`` entry point offers a convenient pipeline that runs all
require steps in order. Use this with small datasets, e.g., for a number
of point locations. Here's a basic example:

.. code-block:: shell

   aris-1go --input input.zarr --output output.zarr

Other available CLIs:

- ``aris-calc-waterbudget``: Calculate water budget
- ``aris-calc-pheno``: Calculate phenology
- ``aris-calc-yield``: Calculate yield expectation

For a large dataset, run them in the following order (e.g. years 2026 2027 2028):

1. ``aris-calc-waterbudget --mode snow 2026 2027 2028``
2. ``aris-calc-pheno 2026 2027 2028``
3. ``aris-calc-waterbudget --mode soil 2026 2027 2028``
4. ``aris-calc-yield --mode both 2026 2027 2028``

API Usage
---------

You can also use ARIS_lite in your own Python routines. After installation, you can:

.. code-block:: python

   from aris_lite import phenology, water_budget, yield_expectation

Troubleshooting
---------------

If you get stuck, please file issues on GitHub.
