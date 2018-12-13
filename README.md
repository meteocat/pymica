[![GitHub release](https://img.shields.io/github/release-pre/meteocat/pymica.svg)](https://github.com/meteocat/pymica/releases)

(py)Meteorological variable Interpolation based on Clustered Analysis
=====================================================================

pyMICA is an interpolation system that combines multiple linear regressions and clustering. The philosophy of MICA is based on an iterative process to reduce the final error of the interpolated field.

The iterativeness of MICA is that there is not a defined number of clusters in which stations are grouped or divided but several number of clusters are considered and the one that performs the best, in terms of RMSE, is selected.

[Try the demo]() |
[Read the docs](https://pymica.readthedocs.io/en/latest)