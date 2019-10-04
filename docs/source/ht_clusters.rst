Create clusters automatically
=============================

MICA system is based on applying different regional regression models.
But before the application of the models, the regions must be defined.
These regions can be delimited by administrative boundaries,
climatically or as in the present case, automatically.

We’ll use the K-Means algorithm to group statations. It is implemented
using `SciKit-Learn <https://scikit-learn.org/stable/>`__ package.

First, we’ll load the required modules from PyMica package, in this
case, ``create_clusters``.

.. code:: ipython3

    from cluster.create_clusters import create_clusters

The ``create_clusters`` function receives two parameters:

1. Stations data file path

   The path of a .json file containing a list of the stations to group.
   Each station must have its identification (id) longitude (lon),
   latitude (lat) and altitude (alt). An example can be seen in
   sample_station_metadata.json which contains
   the automatic weather stations network of the Meteorological Service
   of Catalonia. The first element of the list in the abovementioned
   file is the following:

   .. code:: json

      {"id": "AN", 
       "alt": 7.5,
       "lon": 2.18091,
       "lat": 41.39004}

2. Number of clusters

   The K-Means algorithm allows to chose the resultant number of
   clusters in which the stations are grouped.

Now, we’ll call the ``create_clusters`` function with the .json file
path and with 3 as the resultant number of clusters.

A webservice will prompt up. There you can download the built clusters
in a GeoJSON format. In addition, it’s possible to modify the automatic
classification made by K-Means and then download them with the
modifications.

.. code:: ipython3

    create_clusters('../sample-data/data/smc_metadata.json', 3)

The .json extension downloaded file contains the boundaries of each
cluster. Then, it can be opened with a GIS software and modified by the
user if necessary.