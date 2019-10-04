Step 1: Weather station data and explanatory fields
===================================================

In this tutorial we’ll cover the first steps of PyMica including
preparation of weather station data and explanatory variable fields.

- :ref:`1.1 Preparation of weather station data`
- :ref:`1.2 Generate explanatory data fields`

1.1 Preparation of weather station data
---------------------------------------

The data format of weather stations data used by PyMica is a list
containing a dictionary for each weather station including, at least,
the following vairables:

-  Longitude
-  Latitude
-  Identification code
-  Meteorological variable value to interpolate
-  Value of the explanatory variables that will be used in the multiple
   linear regression calculation (altitude, distance to coast…)

An element of the list containing this variables are organized as
follows for each weather station:

.. code:: json

          {'id': value, 
           'temp': value,
           'lon': value,
           'lat': value,
           'altitude': value,
           ...}

The weather station data is supplied to PyMica in a .json file including
a list containing information of all weather stations to consider.

We’ll work with data from the Automatic Weather Station Network (XEMA)
of the Meteorological Service of Catalonia. Still, you can provide your
own data to PyMica!

First, we’ll import the required libraries.

.. code:: ipython3

    import json
    import pandas as pd
    from datetime import datetime

Now, let’s suppose that our data is in a .csv format. In /cat directory
we’ll find data from XEMA network for 2017/02/21 12:00 UTC and its
corresponding metadata. There are four files, two in .csv format and two
in .json format ready to be used by PyMICA. If you want to skip the
preparation of .json files, just go to :ref:`1.2 Generate explanatory data fields`.

We’ll open both .csv files: XEMA_20170221_1200.csv and XEMA_metadata
using pandas.

.. code:: ipython3

    file_data = '../sample-data/data/XEMA_20170221_1200.csv'
    file_metadata = '../sample-data/data/XEMA_metadata.csv'
    
    station_data = pd.read_csv(file_data)
    metadata = pd.read_csv(file_metadata)
    
    data = []
    for key in station_data['key']:
        df_data = station_data[station_data['key'] == key]
        df_meta = metadata[metadata['key'] == key]
        data.append({'id': key, 
                     'temp': float(df_data['temp']),
                     'lon': float(df_meta['lon']),
                     'lat': float(df_meta['lat']),
                     'altitude': float(df_meta['altitude']),
                     'dist': float(df_meta['dist'])})

If we print the first element of ``data`` we can see all the required
variables for a station (longitude, latitude, distance to coast line,
value of temperature, identification code and altitude):

.. code:: ipython3

    print('Sample data: ' + str(data[0]))
    print('Number of stations: ' + str(len(data)))


.. parsed-literal::

    Sample data: {'id': 'C6', 'temp': 8.8, 'lon': 0.9517200000000001, 'lat': 41.6566, 'altitude': 264.0, 'dist': 0.8587308027349195}
    Number of stations: 180


Now, we’ll save this data into a .json file to use it later.

.. code:: ipython3

    with open('../sample-data/data/smc_data.json', 'w') as outfile:
        json.dump(data, outfile)

It is also important to creata a file with station metadata information.
Then, we’ll use ``metadata`` variable to build a .json file.

.. code:: ipython3

    values = []
    for key in metadata['key']:
        df_meta = metadata[metadata['key'] == key]
        values.append({'id': key,
                       'alt': float(df_meta['altitude']),
                       'lon': float(df_meta['lon']),
                       'lat': float(df_meta['lat']),
                       'dist': float(df_meta['dist'])
                      })

Now, we’ll save this data into a .json file to use it later.

.. code:: ipython3

    with open('../sample-data/data/smc_metadata.json', 'w') as outfile:
        json.dump(values, outfile) 

As you can see, we have introduced distance to coast values in our
metadata .json file and in the .json field containing temperature data.
The reason is that in the present case, we’ll consider distance to coast
as a coefficient in the Multiple Linear Regression models. If you want
your distance to coast values for your stations or know how they are
obtained, please see HOWTO.

This is for the Catalan region, but you can try it with data from any
other region!

We have finished the preparation of weather station data for PyMica!

1.2 Generate explanatory data fields
------------------------------------

The explanatory variables considered in this tutorial are altitude and
distance to coast. Then, we need a Digital Elevation Model (DEM) and a
raster matrix of distance to coast values.

In the cat/explanatory directory there is a DEM of Catalonia available
and we’ll use it for this tutorial. All the explanatory variable raster
matrices must have the same spatial resolution and extension. Then, the
DEM will be used as a reference to build the others, in this case only
the distance to coast raster.

First, we’ll import the necessary libraries.

.. code:: ipython3

    from osgeo import gdal, osr
    from distance.distance_to_sea import get_dist_array

For ``get_dist_array`` function we need four parameters: projection,
geotransform, size and a coast line file. We’ll get the first three from
the DEM and the coast line from explanatory folder.

.. code:: ipython3

    dem_file = '../sample-data/explanatory/cat_dem_25831.tif'
    dem = gdal.Open(dem_file)
    
    projection = 25831
    geotransform = dem.GetGeoTransform()
    size = [dem.RasterXSize, dem.RasterYSize]
    coast_line = '../sample-data/explanatory/cat_coast_line.json'

Once all the parameters are set, we call the ``get_dist_array``
function.

.. code:: ipython3

    d_coast = get_dist_array(proj=projection, geotransform=geotransform, size=size, dist_file=coast_line)


.. parsed-literal::

    Progress: 100%  


Now we can get a quick look of the d_coast array:

.. code:: ipython3

    import matplotlib.pyplot as plt
    plt.imshow(d_coast)
    plt.show()



.. image:: _static/ems_dsea.png


And we must save the array into a .tif file to use it later. To do that,
we’ll define first a function to accomplish that:

.. code:: ipython3

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

    get_tif_from_array(file_path = '../sample-data/explanatory/cat_distance_coast.tif',
                       data = d_coast,
                       geotransform = geotransform,
                       projection = projection)

Now we have all the explanatory variables fields built and we have finished the first tutorial of PyMica!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^