Installation
============

pymica needs the following dependencies:

- python 3.9/3.10
- cython
- numpy
- scipy
- scikit-learn
- gdal
- pyproj
- pyshp
- shapely


There are several ways to install this package.

Anaconda install
----------------

pymica is available in **meteocat** Anaconda channel and it can be installed in your `conda` environment by running in a terminal the following command:

.. code-block:: bash
   
   $ conda install -c meteocat -c conda-forge pymica


pip install
-----------

pymica is also avaialbe in Python package installer `pip` and it can be installed in your environemnt by running in a terminal the following command:

.. code-block:: bash

   $ pip install -r requirements.txt
   $ pip install pymica

Install from source
-------------------

To install pymica from source it is recommended to use `pip` instead of `setup.py`.

.. code-block:: bash

   $ pip install ./pymica
