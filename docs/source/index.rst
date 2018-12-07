.. pyRASP documentation master file, created by
   sphinx-quickstart on Wed Oct  3 12:51:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyMICA's documentation!
==================================

MICA, the acronym of Meteorological field Interpolation based on Clustered Analysis is
an interpolation system that combines multiple linear regressions and clustering. The 
philosophy of MICA is based on an iterative process to reduce the final error of the 
interpolated field.

The iterativeness of MICA is that there is not a defined number of clusters in which 
stations are grouped or divided but several number of clusters are considered and 
the one that performs the best, in terms of RMSE, is selected. 

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   installation
   calculate_field
   regression
   interpolation
   howitworks
   theory


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`