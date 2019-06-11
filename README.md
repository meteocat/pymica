[![GitHub release](https://img.shields.io/github/release-pre/meteocat/pymica.svg)](https://github.com/meteocat/pymica/releases)
[![Documentation Status](https://readthedocs.org/projects/pymica/badge/?version=latest)](https://pymica.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/meteocat/pymica.svg?branch=master)](https://travis-ci.org/meteocat/pymica)

[![Logo](docs/source/_static/logo.svg)](#)

(py)Meteorological variable Interpolation based on Clustered Analysis
=====================================================================

pyMICA is an interpolation system that combines multiple linear regressions and clustering. The philosophy of MICA is based on an iterative process to reduce the final error of the interpolated field.

The iterativeness of MICA is that there is not a defined number of clusters in which stations are grouped or divided but several number of clusters are considered and the one that performs the best, in terms of RMSE, is selected.


What is MICA and how it works?
================================
MICA spatially interpolates meteorological surface observations through multiple linear regressions (MLR) and residual corrections. Two options are available: using a simple MLR for all the surface observations or divide them in clusters.

The first option implies the calculation of a MLR considering all the observations at once and using explanatory variables, such as altitude, distance to coast, latitude and longitude. The second option, uses clusters to classify stations in different groups. This allows to separate stations that may behave differently due to the presence of dissimilar weather conditions. For example, weather stations placed at similar altitude, but ones under the effects of fog and others with clear sky conditions.

A complete explanation of how it works and the idea behind MICA can be found in [pyMICA documentation](https://pymica.readthedocs.io/en/latest/howitworks.html)


Installation
============

To install pyMICA you can have a look at [pyMICA installation](https://pymica.readthedocs.io/en/latest/installation.html).


Use
===

A set of [examples]() were designed to explore the different possibilities of MICA.

Another repository was created to store jupyter notebooks [examples]()


[Try the demo]() |
[Read the docs](https://pymica.readthedocs.io/en/latest)