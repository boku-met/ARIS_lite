Usage Guide
============

Overview
--------

This guide explains how to use the ARIS-lite package to compute plant
stress indicators from modelling the soil water balance using
meteorological data.

Main Components
---------------

ARIS-lite consists of the following modules:

- ``water_budget.py``: Handles soil water balance calculations
- ``phenology.py``: Implements phenological models
- ``yield_expectation.py``: Calculates crop yield expectations

Basic Usage
-----------

To use ARIS-lite, you can either:

1. Use the command-line interfaces (CLIs) provided by the package
2. Import and use the functions programmatically

In any case, first make sure your data is organized in Zarr stores with
the correct variable names and with the correct units. The list below
may be incomplete - in that case, refer to the source code. If not
specified, the variables correspond to daily aggregates at 2 m above the
surface, with temperatures in ``degC``.

- ``air_temperature``: Average air temperature
- ``max_air_temp``: Maximum air temperature
- ``min_air_temp``: Minimum air temperature
- ``rel_humidity``: Average relative humidity in %
- ``min_rel_hum``: Minimum relative humidity in %
- ``precipitation``: Total precipitation in mm water equivalent
- ``wind_speed``: Wind speed in m/s 10 m above the surface
- ``pot_evapotransp``: Average potential evapotranspiration in mm water equivalent

Command-Line Usage
------------------

The canonical CLI is now rooted at ``aris``.

For in-memory runs on smaller datasets, use:

.. code-block:: shell

   aris 1go "winter wheat" "maize" input.zarr output.zarr

For yearly staged processing, use ``aris calc`` subcommands:

.. code-block:: shell

   aris calc waterbudget --mode snow 2026 2027 2028
   aris calc pheno 2026 2027 2028
   aris calc waterbudget --mode soil 2026 2027 2028
   aris calc yield --mode both 2026 2027 2028 \
     --yield-max PATH --yield-intercept PATH --yield-params PATH

Path conventions for staged calculations default to ``../data`` and can be
changed with ``--base-dir``.

Legacy command migration
~~~~~~~~~~~~~~~~~~~~~~~~

+----------------------------------+----------------------------------+
| Legacy command                   | Canonical replacement            |
+==================================+==================================+
| ``aris-1go``                     | ``aris 1go``                     |
+----------------------------------+----------------------------------+
| ``aris-calc-waterbudget``        | ``aris calc waterbudget``        |
+----------------------------------+----------------------------------+
| ``aris-calc-pheno``              | ``aris calc pheno``              |
+----------------------------------+----------------------------------+
| ``aris-calc-yield``              | ``aris calc yield``              |
+----------------------------------+----------------------------------+

Deprecation policy
~~~~~~~~~~~~~~~~~~

Legacy flat commands and legacy high-level module-level functions
(``main*`` and ``cli`` aliases) remain available in ``0.3.x``, emit
deprecation warnings, and will be removed in ``0.4.0``.


API Usage
---------

You can also use ARIS-lite in your own Python routines. After installation, you can:

.. code-block:: python

   from aris_lite import phenology, water_budget, yield_expectation

Troubleshooting
---------------

If you get stuck, please file issues on GitHub.
