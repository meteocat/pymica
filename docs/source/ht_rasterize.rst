Rasterize clusters
==================

Once the clusters are defined, either automatically or following other
criteria, they must be rasterized to be used by the pyMICA functions.

In this section cluster polygons are rasterized and blurred. Raster
matrices obtained are 1 inside the polygon area and 0 outside of it. In
order to avoid a sharp transition when merging clusters, a blurring
effect is performed.

For this purpose we’ll use the ``rasterize_clusters`` function which
receives a .json file path and a ``Dict`` with the output properties as
parameters. Therfore, we’ll import ``rasterize_clusters`` function from
create_cluster_files.py module. In addition,
``create_repreojected_geoms`` will be also imported to transform
longitude and latitude coordinates projection into UTM.

.. code:: ipython3

    from cluster.create_cluster_files import rasterize_clusters, create_reprojected_geoms

First, we’ll use ``create_reprojected_geoms`` to transform the clusters
.json file projection from longitude and latitude coordinates to a
desired EPSG. In the present case, 25831. We’ll keep the output of this
function to pass it as a parameter in ``rasterize_clusters`` function.

.. code:: ipython3

    clusters_layer = create_reprojected_geoms('../sample-data/clusters/clusters_4.json', 25831)

Now we’ll rasterize the above layer. ``rasterize_clusters`` function
receives two parameters:

1. Clusters .json file path or an ogr datasource object.

   A file with clusters boundaries with the same format to that obtained
   in the above Section. It can be the one obtained automatically or a
   set of clusters designed by the user. It can also receive and ogr
   datasource object.

2. Output properties

   | out_file : the output file path and name.
   | size : the output raster size.
   | geotransform: the output raster geotransform.

We’ll pass the ``clusters_layer`` obtained layer as the first parameter
of the ``rasterize_clusters`` function.

In this case we’ll set out_file as
``'../sample-data/clusters/rasterized_clusters_test'``. The two
remaining parameters will be set in accordance with the extent and
resolution of the final interpolated field we want to obtain. In this
example:

.. code:: ipython3

    out_properties = {'out_file'    : '../sample-data/clusters/rasterized_clusters_test',
                      'size'        : [1000, 970],
                      'geotransform': [260000, 270, 0, 4750000, 0, -270]}

Now, we call the ``rasterize_clusters`` function.

.. code:: ipython3

    rasterize_clusters(clusters_layer, out_properties)

The clusters have been rasterized and saved as a .tiff