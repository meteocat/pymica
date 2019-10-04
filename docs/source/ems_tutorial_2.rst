
Tutorial 2: Distance to coast calculations
==========================================

In this notebook, we’ll show how to calculate the distances between the
stations of our network to a coast line and transform it with an
exponential function. In addition, we’ll obtain a distance to coast
field ready to use it as an explanatory variable for interpolation
purposes.

Calculate distance from stations to the coastline
-------------------------------------------------

If we want to know the distance to coast in meters of every station in
our network, ``get_distances`` function provides it. Then, once the
distances are known, the following logarithmic function (``dist2func``)
is used to get the distance to coast function value.

:math:`d_{coast} = 1 - e^{-\dfrac{3\cdot dist}{D}}`,

where :math:`d_{coast}` is the resultant distance to coast of the
function, *dist* is the Euclidean distance from a point to the coast
line and *D* is the distance where the distance to coast is cancelled.

First we’ll import both functions (``get distances`` and ``dist2func``)
and then call them.

.. code:: ipython3

    from distance.distance_to_sea import get_distances, dist2func

``get_distances`` receives as parameters a list of longitude and
latitude points. As an example we’ll calculate the distance to coast
function value for two stations. One with longitude 1\ :math:`^{\circ}`
and latitude 41\ :math:`^{\circ}`, and another one with
0.5\ :math:`^{\circ}` and 40\ :math:`^{\circ}` for longitude and
latitude, respectively.

First, we calculate the distances to coast in meters.

.. code:: ipython3

    points = [[1, 41], [0.5, 40]]
    dist_file = '../sample-data/explanatory/cat_coast_line.json'
    dcoast_points = get_distances(points, dist_file)
    print('Station 1: ' + str(dcoast_points[0]) + ' m')
    print('Station 2: ' + str(dcoast_points[1]) + ' m')


.. parsed-literal::

    Station 1: 3910.667706725694 m
    Station 2: 30695.846524391513 m


Now, with the ``dcoast_points``, we can call ``dist2func`` which apply
the abovementioned logarithmic function.

.. code:: ipython3

    print('Distance to coast function:')
    for i in range(len(dcoast_points)):
        print('    Station ' + str(i+1) + ': ' + str(dist2func(dcoast_points[i])))


.. parsed-literal::

    Distance to coast function:
        Station 1: 0.11069945630424916
        Station 2: 0.6018296681315223


Create distance to coast explanatory field
------------------------------------------

The distance to coast raster is built using ``get_dist_array`` function.
Now, we’ll import it.

.. code:: ipython3

    from distance.distance_to_sea import get_dist_array

The ``get_dist_array`` function returns a matrix with the distance to
sea values. It receives as parameters:

-  proj : The EPSG code for the output matrix projection
-  geotransform: The output raster geotransform
-  size : The output raster size
-  dist_file : The path to an ogr compatible file with a line containing
   the shore geometry

Now, we’ll call the ``get_dist_array_function``.

.. code:: ipython3

    dist_file = '../sample-data/explanatory/cat_coast_line.json'
    dcoast_array = get_dist_array(proj=25831,
                                  geotransform=[260000, 270, 0, 4750000, 0, -270],
                                  size=[1000, 970],
                                  dist_file=dist_file)


.. parsed-literal::

    Progress: 100%  


Now we’ll save the ``dcoast_array`` as a .tiff image in order to keep it
for further steps in pyMICA. For this purpose, we’ll define the
``get_tif_from_array`` function and then, call it. It requires the
destination file path with the name of the file included, the data to
include in the .tiff, the geotransform and the EPSG projection of the
.tif file.

.. code:: ipython3

    from osgeo import gdal, osr
    
    def get_tif_from_array(file_path, data, geotransform, projection):
        '''
        Reads an array and returns a .tif
        Args:
            file_path (str): The path of the .tiff file to be saved
            data (array): Array of data to be transformed
            geotransform (array): Geotransform for the .tif file
            projection (int): EPSG projection code of the .tif file
        '''
        driver = gdal.GetDriverByName('GTiff')
        ds_out = driver.Create(file_path, data.shape[1], data.shape[0], 1, gdal.GDT_Float32)
        ds_out.GetRasterBand(1).WriteArray(data)
        ds_out.GetRasterBand(1).SetNoDataValue(0)
        ds_out.SetGeoTransform(geotransform)
        spatialRef = osr.SpatialReference()
        spatialRef.ImportFromEPSG(projection)
        ds_out.SetProjection(str(spatialRef))
    
        ds_out = None

.. code:: ipython3

    get_tif_from_array(file_path = '../sample-data/results/dcoast_sample.tif',
                       data = dcoast_array,
                       geotransform = [260000, 270, 0, 4750000, 0, -270],
                       projection = 25831)

Now, a .tif file including the dcoast_array is saved in
./notebooks/preprocessing/dcoast.tiff

If we want to have a quick look on dcoast_array we can plot it using
imshow.

.. code:: ipython3

    import matplotlib.pyplot as plt
    plt.imshow(dcoast_array)
    plt.show()



.. image:: _static/ems_dsea.png


The required raster fields where the regression models will be applied
have been created.