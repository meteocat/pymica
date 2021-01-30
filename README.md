![PyPI](https://img.shields.io/pypi/v/pymica.svg)
[![Anaconda-Server Badge](https://anaconda.org/meteocat/pymica/badges/version.svg)](https://anaconda.org/meteocat/pymica)
[![Documentation Status](https://readthedocs.org/projects/pymica/badge/?version=latest)](https://pymica.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/meteocat/pymica.svg?branch=master)](https://travis-ci.org/meteocat/pymica)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/meteocat/pymica-examples/master?urlpath=/lab/tree/index.ipynb)

[![Logo](https://github.com/meteocat/pymica/blob/master/docs/source/_static/logo.svg)](#)

(py)Meteorological variable Interpolation based on Clustered data Analysis
==========================================================================

pyMICA is an interpolation system that combines multiple linear regressions and clustering. The philosophy of MICA is based on an iterative process to reduce the final error of the interpolated field.

The iterativeness of MICA is that there is not a defined number of clusters in which stations are grouped or divided but several number of clusters are considered and the one that performs the best, in terms of RMSE, is selected.

What is MICA and how it works
-----------------------------
MICA spatially interpolates meteorological surface observations through multiple linear regressions (MLR) and residual corrections. Two options are available: using a simple MLR for all the surface observations or divide them in clusters.

The first option implies the calculation of a MLR considering all the observations at once and using explanatory variables, such as altitude, distance to coast, latitude and longitude. The second option uses clusters to classify stations in different groups. This allows to separate stations that may behave differently due to the presence of dissimilar weather conditions. For example, weather stations placed at a similar altitude, ones under the effects of fog and others with clear sky conditions.

A complete explanation of how it works and the idea behind MICA can be found in [pyMICA documentation](https://pymica.readthedocs.io/en/latest/howitworks.html)

If you use pyMICA, please cite us as:

[Casellas, E., Bech, J., Veciana, R., Miró, J. R., Sairouni, A., & Pineda, N. (2020). A meteorological analysis interpolation scheme for high spatial-temporal resolution in complex terrain. Atmospheric Research, 246, 105103.](https://www.sciencedirect.com/science/article/pii/S0169809520304166?via%3Dihub)

Installation
------------

To install pyMICA you can have a look at [pyMICA installation](https://pymica.readthedocs.io/en/latest/installation.html) documentation.

Use
---

A set of examples were designed to explore the different possibilities of MICA.

Another repository was created to store sample data and the examples in jupyter notebooks [pymica-examples](https://github.com/meteocat/pymica-examples)

[Try the demo](https://mybinder.org/v2/gh/meteocat/pymica-examples/master?urlpath=/lab/tree/index.ipynb) |
[Read the docs](https://pymica.readthedocs.io/en/latest)
