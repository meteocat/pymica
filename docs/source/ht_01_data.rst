01. Weather station data
========================

In this tutorial we’ll cover the preparation of weather station data to use it in pymica.

The data format of weather stations data used by PyMica is a list
containing a dictionary for each weather station including, at least,
the following variables:

-  id: identification code.
-  lon: longitude coordinate.
-  lat: latitude coordinate.
-  value: observation value.

It can also contain other keys referring to the variables used in the interpolation, such as altitude or distance to coast. Altitude must be named 'altitude', the rest of explanatory variables do not need a specific name in pymica.

An element of the list containing this variables are organized as
follows for each weather station:

.. code:: json

          {'id': id_code, 
           'lon': longitude coordinate value,
           'lat': latitude coordinate value,
           'value': value,
           'altitude': altitude value,
           ...}

The weather station data is supplied to :py:meth:`pymica.pymica.PyMica.interpolate()` as a list of dictionaries, one for each station.

As an example, we'll work from the Automatic Weather Station Network (XEMA)
of the Meteorological Service of Catalonia (`XEMA <https://www.meteo.cat/observacions/xema>`_). Still, you can provide your
own data to PyMica.

First, we’ll import the required libraries.

.. code-block:: python

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

.. code-block:: python

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

.. code-block:: python

    print('Sample data: ' + str(data[0]))
    print('Number of stations: ' + str(len(data)))


.. parsed-literal::

    Sample data: {'id': 'C6', 'temp': 8.8, 'lon': 0.9517200000000001, 'lat': 41.6566, 'altitude': 264.0, 'dist': 0.8587308027349195}
    Number of stations: 180