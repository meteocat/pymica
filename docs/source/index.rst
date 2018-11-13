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

The starting point of MICA was the former operational real-time air temperature and 
relative humidity spatial interpolation methodology in the Meteorological Service of
Catalonia (SMC). This was based in the calculation of a Multiple Linear Regression using 
all stations from XEMA network and an anomaly correction of the residues. Two explanatory 
variables were considered: altitude and distance to coast. Then, the residues of the MLR, 
which are the difference between the predicted and observed values, were interpolated through
an inverse of the distance procedure. Performance of the interpolation was assessed 
by Root Mean Square Error (RMSE) considering the residues of the MLR. 

In order to improve the interpolation performance an iterative process was designed 
combining clustering of stations and MLRs with anomaly corrections. The iterativeness of 
the methodology proposed is that there is not a defined number of clusters in which stations 
are grouped or divided but several number of clusters are considered and the one that 
performs the best is selected. 

The MICA system can be divided in two parts. The first one involves the definition of
clusters and the explanatory variables that are going to be used in the MLR calculations. 
The second one is based on the choice of the best number of clusters and on obtaining the 
final variable of interest field.

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
