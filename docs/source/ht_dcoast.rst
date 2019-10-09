Calculate distance from stations to coast line
==============================================

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

.. code-block:: python

    from distance.distance_to_sea import get_distances, dist2func

``get_distances`` receives as parameters a list of longitude and
latitude points. As an example we’ll calculate the distance to coast
function value for two stations. One with longitude 1\ :math:`^{\circ}`
and latitude 41\ :math:`^{\circ}`, and another one with
0.5\ :math:`^{\circ}` and 40\ :math:`^{\circ}` for longitude and
latitude, respectively.

First, we calculate the distances to coast in meters.

.. code-block:: python

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

.. code-block:: python

    print('Distance to coast function:')
    for i in range(len(dcoast_points)):
        print('    Station ' + str(i+1) + ': ' + str(dist2func(dcoast_points[i])))


.. parsed-literal::

    Distance to coast function:
        Station 1: 0.11069945630424916
        Station 2: 0.6018296681315223
