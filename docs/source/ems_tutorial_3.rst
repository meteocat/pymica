
Tutorial 3: Automatic creation and rasterization of clusters
============================================================

Tutorial 3.1 : Create clusters automatically
--------------------------------------------

Weather stations can be grouped following different criteria. One of
them consists of defining groups automatically considering machine
learning techniques. In the present case, we will use the K-Means
algorithm to classify stations, which is implemented using the
`SciKit-Learn <https://scikit-learn.org/stable/>`__ package.

First, we will load the required modules from PyMica package, in this
case, ``create_clusters``.

.. code:: ipython3

    from cluster.create_clusters import create_clusters

The ``create_clusters`` function receives two parameters:

1. Stations data file path

   The path of a .json file containing a list of the stations to group.
   Each station must have its identification (id) longitude (lon),
   latitude (lat) and altitude (alt). An example can be seen in
   sample_station_metadata.json (REF github al fitxer) which contains
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

``create_clusters('../sample-data/data/smc_metadata.json', 3)``

After executing the previous code line, a webservice prompts up, where
the build clusters are shown and can be downloaded in a GeoJSON format
for further applications. Once downladed, they can be opened by a GIS
software and easily modified.

In this case, we did not make the last code line executable since it is
not possible to open a browser from this jupyter notebook. Therefore,
this script must be executed from command line after cloning the github
`pymica-examples <https://github.com/meteocat/pymica-examples>`__
repository in your computer.

However, the follwing image shows how the webservice looks like:



In this case, we downloaded the clusters file and save it into
``clusters`` folder as ``clusters-3.json``

Tutorial 3.2: Rasterize clusters
--------------------------------

The clusters are defined as polygons, but they must be rasterized to be
used by pyMICA functions. Therefore, in this section we will show how
the cluster polygons are rasterized and blurred. For each cluster we
will obtain a raster matrix with a value of 1 inside the polygon
boundary and 0 outside of it, which is then blurred to avoid sharp
transition when clusters are merged.

For this purpose we will use the ``rasterize_clusters`` function which
receives a .json file path and a ``Dict`` with the output properties as
parameters. Therfore, we will import ``rasterize_clusters`` function
from ``create_cluster_files`` module. In addition,
``create_repreojected_geoms`` will be also imported to transform
longitude and latitude coordinates projection into UTM.

.. code:: ipython3

    from cluster.create_cluster_files import rasterize_clusters, create_reprojected_geoms

First, we will use ``create_reprojected_geoms`` to transform the
``clusters-3.json`` file projection from longitude and latitude
coordinates to a desired EPSG. In the present case, 25831. We will keep
the output of this function to pass it as a parameter in
``rasterize_clusters`` function.

.. code:: ipython3

    clusters_layer = create_reprojected_geoms('../envmodsoft/clusters/clusters-3.json', 25831)

Now we will rasterize the above layer with the ``rasterize_clusters``
function, which receives two parameters:

1. Clusters .json file path or an ogr datasource object.

   A file with clusters boundaries with the same format to that obtained
   in the above Section. It can be the one obtained automatically or a
   set of clusters designed by the user. It can also receive and ogr
   datasource object.

2. Output properties

   | out_file : the output file path and name.
   | size : the output raster size.
   | geotransform: the output raster geotransform.

We will pass the ``clusters_layer`` obtained layer as the first
parameter of the ``rasterize_clusters`` function.

In this case we’ll set out_file as ``'clusters/rasterized-clusters-3'``.
The two remaining parameters will be set in accordance with the extent
and resolution of the final interpolated field we want to obtain. In
this case:

.. code:: ipython3

    out_properties = {'out_file'    : '../envmodsoft/clusters/rasterized-clusters-3',
                      'size'        : [1000, 970],
                      'geotransform': [260000, 270, 0, 4750000, 0, -270]}

Now, we call the ``rasterize_clusters`` function.

.. code:: ipython3

    rasterize_clusters(clusters_layer, out_properties)

The clusters have been rasterized and saved as a .tiff file