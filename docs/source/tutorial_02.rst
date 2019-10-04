Step 2: Clusters
================

This tutorial is focused on clusters creation and on building associated
raster matrices.

-  :ref:`2.1 Creation of automatic clusters`
-  :ref:`2.2 Rasterize the clusters`

2.1 Creation of automatic clusters
----------------------------------

In this tutorial we’ll classify a weather stations network in two
different number of clusters. First, we’ll group the stations in two
clusters and then in four, using the K-Means algorithm.

What we need for this step? Station data including longitude, latitude
and altitude that we’ll get from the smc_metadata.json file. But first, 
we’ll import the required libraries.

.. code:: ipython3

    from cluster.create_clusters import create_clusters

The ``create_clusters`` function requires two parameters: a .json file
including station metadata and the number of clusters we want to obtain.

Firstly, we’ll create two clusters. When calling ``create_clusters``
function, a new tab will be opened in your browser from which clusters
can be downloaded in a .json file which we’ll save in
./docs/notebooks/tutorials/cat/clusters/.

``create_clusters('../sample-data/data/smc_metadata.json', 2)``

We repeat the process for number of clusters 4.

``create_clusters('../sample-data/data/smc_metadata.json', 4)``

We have finished this step of the tutorial, now we have to rasterize the
clusters!

2.2 Rasterize the clusters
--------------------------

Clusters must be rasterized in order to be used by PyMica functions. The
rasterized clusters are used to obtain the interpolated field.

For this part we’ll call ``rasterize_clusters``, but first we need to
reproject the clusters built to the desired EPSG projection using
``create_reprojected_geoms``, which in this case is EPSG:25831.

We’ll use the clusters saved in
./docs/notebooks/tutorials/cat/clusters/, but first we must import the
required libraries.

.. code:: ipython3

    from cluster.create_cluster_files import rasterize_clusters, create_reprojected_geoms

Now we call the ``create_reprojected_geoms`` which requires the clusters
.json file path and an EPSG code. We call it twice for the two number of
clusters chosen in :ref:`2.1 Creation of automatic clusters`.

.. code:: ipython3

    clusters_2_layer = create_reprojected_geoms('../sample-data/clusters/clusters_2.json', 25831)
    clusters_4_layer = create_reprojected_geoms('../sample-data/clusters/clusters_4.json', 25831)

Once the layers are reprojected, they are ready to be reprojected, so we
call ``rasterize_clusters``. This function requires two parameters: the
clusters layer and a dictionary with the raster properties (name of the
output file, size and geotransform.

In this case we will use the same values of the DEM file.

.. code:: ipython3

    from osgeo import gdal
    dem_file = '../sample-data/explanatory/cat_dem_25831.tif'
    dem = gdal.Open(dem_file)
    geotransform = dem.GetGeoTransform()
    size = [dem.RasterXSize, dem.RasterYSize]
    
    out_properties_2 = {'out_file'    : '../sample-data/clusters/clusters_2_mask',
                      'size'        : size,
                      'geotransform': geotransform}
    
    out_properties_4 = {'out_file'    : '../sample-data/clusters/clusters_4_mask',
                      'size'        : size,
                      'geotransform': geotransform}

Now that the ``out_properties`` are defined for the two number of
clusters considered, we call ``rasterize_clusters`` function.

.. code:: ipython3

    rasterize_clusters(clusters_2_layer, out_properties_2)
    rasterize_clusters(clusters_4_layer, out_properties_4)

We have finished all the necessary steps to start working with PyMica!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^