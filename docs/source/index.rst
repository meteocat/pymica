.. pyRASP documentation master file, created by
   sphinx-quickstart on Wed Oct  3 12:51:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/logo.svg

Welcome to pyMICA's documentation!
==================================

MICA, the acronym of Meteorological field Interpolation based on Clustered 
data Analysis is a Python library which interpolates meteorological surface 
observations through multiple linear regressions (MLR) and residual corrections.
Two options are available: using a simple MLR for all the surface observations
or divide them in clusters.

The first option implies the calculation of a MLR considering all the observations
at once and using explanatory variables, such as altitude, distance to coast,
latitude and longitude. The second option, uses clusters to classify stations
in different groups. This allows to separate stations that may behave differently
due to the presence of dissimilar weather conditions. 
For example, weather stations placed at a similar altitude, ones under the effects
of fog and others with clear sky conditions.

Try it yourself! `Jupyter Notebooks <https://github.com/meteocat/pymica-examples>`__

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   installation
   howitworks
   theory
   scripts
   api
   tutorials


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`