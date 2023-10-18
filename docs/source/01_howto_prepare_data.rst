01. Preparing Weather Station Data for PyMica
=============================================

In this tutorial, we’ll cover the preparation of weather station data
for use in PyMica.

The data format for weather station data used by PyMica is a list
containing a dictionary for each weather station, including at least the
following variables:

-  ``id``: Identification code.
-  ``lon``: Longitude coordinate.
-  ``lat``: Latitude coordinate.
-  ``value``: Observation value.

It can also contain other keys referring to the variables used in
interpolation, such as altitude or distance to the coast. Altitude must
be named ‘altitude’; the names of other explanatory variables do not
need to be specific in PyMica.

An element of the list containing these variables is organized as
follows for each weather station:

::

   {
       "id": "id_code",
       "lon": "longitude coordinate value",
       "lat": "latitude coordinate value",
       "value": "value",
       "altitude": "altitude value"
   }

The weather station data is supplied to 
:py:meth:`pymica.pymica.PyMica.interpolate()` as a list of dictionaries, one
for each station.

As an example, we’ll work with data from the Automatic Weather Station
Network (XEMA) of the Meteorological Service of Catalonia
(`XEMA <https://www.meteo.cat/observacions/xema>`__). However, you can
also provide your own data to PyMica.

First, let’s import the required library.

.. code:: python

    import pandas as pd

Now, let’s suppose that our data is in a .csv format. In the
``sample-data/data`` directory, we’ll find data from the XEMA network
for 2017/02/21 12:00 UTC and its corresponding metadata.

We’ll open both .csv files, ``XEMA_20170221_1200.csv`` and
``XEMA_metadata.csv``, using the pandas library and present the head of
data file.

.. code:: python

    file_data = 'sample-data/data/XEMA_20170221_1200.csv'
    file_metadata = 'sample-data/data/XEMA_metadata.csv'
    
    station_data = pd.read_csv(file_data)
    metadata = pd.read_csv(file_metadata)
    
    station_data.head()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>key</th>
          <th>altitude</th>
          <th>dist</th>
          <th>hr</th>
          <th>lat</th>
          <th>lon</th>
          <th>temp</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>C6</td>
          <td>264.0</td>
          <td>0.858731</td>
          <td>80.0</td>
          <td>41.65660</td>
          <td>0.95172</td>
          <td>8.8</td>
        </tr>
        <tr>
          <th>1</th>
          <td>C7</td>
          <td>427.0</td>
          <td>0.839116</td>
          <td>86.0</td>
          <td>41.66695</td>
          <td>1.16234</td>
          <td>7.1</td>
        </tr>
        <tr>
          <th>2</th>
          <td>C8</td>
          <td>554.0</td>
          <td>0.825381</td>
          <td>76.0</td>
          <td>41.67555</td>
          <td>1.29609</td>
          <td>9.3</td>
        </tr>
        <tr>
          <th>3</th>
          <td>C9</td>
          <td>240.0</td>
          <td>0.448604</td>
          <td>47.0</td>
          <td>40.71825</td>
          <td>0.39988</td>
          <td>15.7</td>
        </tr>
        <tr>
          <th>4</th>
          <td>CC</td>
          <td>626.0</td>
          <td>0.849968</td>
          <td>47.0</td>
          <td>42.07398</td>
          <td>2.20862</td>
          <td>15.2</td>
        </tr>
      </tbody>
    </table>
    </div>



And we also present the head of metedata.

.. code:: python

    metadata.head()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>key</th>
          <th>altitude</th>
          <th>dist</th>
          <th>lat</th>
          <th>lon</th>
          <th>name</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>C6</td>
          <td>264.0</td>
          <td>0.858731</td>
          <td>41.65660</td>
          <td>0.95172</td>
          <td>Castellnou de Seana</td>
        </tr>
        <tr>
          <th>1</th>
          <td>C7</td>
          <td>427.0</td>
          <td>0.839116</td>
          <td>41.66695</td>
          <td>1.16234</td>
          <td>Tàrrega</td>
        </tr>
        <tr>
          <th>2</th>
          <td>C8</td>
          <td>554.0</td>
          <td>0.825381</td>
          <td>41.67555</td>
          <td>1.29609</td>
          <td>Cervera</td>
        </tr>
        <tr>
          <th>3</th>
          <td>C9</td>
          <td>240.0</td>
          <td>0.448604</td>
          <td>40.71825</td>
          <td>0.39988</td>
          <td>Mas de Barberans</td>
        </tr>
        <tr>
          <th>4</th>
          <td>CC</td>
          <td>626.0</td>
          <td>0.849968</td>
          <td>42.07398</td>
          <td>2.20862</td>
          <td>Orís</td>
        </tr>
      </tbody>
    </table>
    </div>



Now, let’s prepare the data in the format required by PyMICA, selecting
the air temperature variable (``temp``) and using ``altitude`` and
``dist`` as predictor variables. The variable ``dist`` refers to the
distance from a station to the coastline to account for proximity to sea
influence.

.. code:: python

    data = []
    for key in station_data['key']:
        df_data = station_data[station_data['key'] == key]
        df_meta = metadata[metadata['key'] == key]
        data.append(
            {
                'id': key, 
                'lon': float(df_meta['lon'].iloc[0]),
                'lat': float(df_meta['lat'].iloc[0]),
                'value': float(df_data['temp'].iloc[0]),
                'altitude': float(df_meta['altitude'].iloc[0]),
                'dist': float(df_meta['dist'].iloc[0])
            }
        )

If we print the first element of ``data``, we can see all the required
variables for a station, which include identification code, longitude,
latitude, temperature value, altitude, and distance to the coastline.

.. code:: python

    print('Sample data: ', data[0])
    print('Number of points: ', len(data))


.. parsed-literal::

    Sample data:  {'id': 'C6', 'lon': 0.95172, 'lat': 41.6566, 'value': 8.8, 'altitude': 264.0, 'dist': 0.8587308027349195}
    Number of points:  180


We have now completed this tutorial on how to prepare raw observation
station data to be ready to feed the PyMICA class.
