.. pyRASP documentation master file, created by
   sphinx-quickstart on Wed Oct  3 12:51:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pymica
======

Pymica is a Python library that performs meteorological observation interpolation
using various available methodologies: inverse distance weighting, linear regression,
multiple linear regression (MLR), and residuals correction. Additionally, the MLR
method offers the capability to classify observations into different clusters and
compute a specific MLR model for each cluster. This is particularly effective for
high spatial and temporal resolution observations, especially when some of them are
concurrently influenced by fog, while others experience clear sky conditions. This
approach is also useful in regions affected by or prone to thermal inversions.

More information can be found in `A meteorological analysis interpolation scheme for high spatial-temporal resolution in complex terrain <https://doi.org/10.1016/j.atmosres.2020.105103>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   installation
   methodologies
   tutorials
   ht_explanatory
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`