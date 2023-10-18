[![Anaconda-Server Badge](https://anaconda.org/meteocat/pymica/badges/version.svg)](https://anaconda.org/meteocat/pymica)
[![Documentation Status](https://readthedocs.org/projects/pymica/badge/?version=latest)](https://pymica.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/meteocat/pymica-examples/master?urlpath=/lab/tree/00_index.ipynb)

<img src="https://github.com/meteocat/pymica/blob/master/docs/source/_static/logo_lbug.png" alt="drawing" width="300"/>


(py)Meteorological variable Interpolation based on Clustered data Analysis
==========================================================================

Pymica is a Python library that performs meteorological observation interpolation using various available methodologies: inverse distance weighting, linear regression, multiple linear regression (MLR), and residuals correction. Additionally, the MLR method offers the capability to classify observations into different clusters and compute a specific MLR model for each cluster. This is particularly effective for high spatial and temporal resolution observations, especially when some of them are concurrently influenced by fog, while others experience clear sky conditions. This approach is also useful in regions affected by or prone to thermal inversions.

A complete explanation of how it works and the idea behind MICA can be found in [pyMICA documentation](https://pymica.readthedocs.io/en/latest/howitworks.html).

More information can be found in [A meteorological analysis interpolation scheme for high spatial-temporal resolution in complex terrain.](https://doi.org/10.1016/j.atmosres.2020.105103).

If you use pyMICA, please cite us as:

[Casellas, E., Bech, J., Veciana, R., Miró, J. R., Sairouni, A., & Pineda, N. (2020). A meteorological analysis interpolation scheme for high spatial-temporal resolution in complex terrain. Atmospheric Research, 246, 105103.](https://www.sciencedirect.com/science/article/pii/S0169809520304166?via%3Dihub)


Installation
------------

To install pyMICA you can have a look at [pyMICA installation](https://pymica.readthedocs.io/en/latest/installation.html) documentation.

Use
---

A set of examples were designed to explore the different possibilities of MICA.

Another repository was created to store sample data and the examples in jupyter notebooks [pymica-examples](https://github.com/meteocat/pymica-examples)

[Try the demo](https://mybinder.org/v2/gh/meteocat/pymica-examples/master?urlpath=/lab/tree/00_index.ipynb) |
[Read the docs](https://pymica.readthedocs.io/en/latest)
