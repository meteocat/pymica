![PyPI](https://img.shields.io/pypi/v/pymica.svg)
[![Documentation Status](https://readthedocs.org/projects/pymica/badge/?version=latest)](https://pymica.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/meteocat/pymica.svg?branch=master)](https://travis-ci.org/meteocat/pymica)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/meteocat/pymica-examples/master?urlpath=/lab/tree/index.ipynb)

[![Logo](https://raw.githubusercontent.com/meteocat/pymica-examples/master/docs/source/_static/logo.svg)](#)

(py)Meteorological variable Interpolation based on Clustered Analysis
=====================================================================

pyMICA is an interpolation system that combines multiple linear regressions and clustering. The philosophy of MICA is based on an iterative process to reduce the final error of the interpolated field.

The iterativeness of MICA is that there is not a defined number of clusters in which stations are grouped or divided but several number of clusters are considered and the one that performs the best, in terms of RMSE, is selected.

[Try the demo](https://mybinder.org/v2/gh/meteocat/pymica-examples/master?urlpath=/lab/tree/index.ipynb) |
[Read the docs](https://pymica.readthedocs.io/en/latest)