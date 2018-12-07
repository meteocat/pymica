Clustering of weather stations
==============================

.. _d3delaunay: https://github.com/d3/d3-delaunay
.. _sklearn: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

In this section the process followed to classify weather stations in automatically
defined clusters is explained. The building clusters procedure involves four
steps:

1. :ref:`Weather stations classification`
2. :ref:`Delaunay triangulation`
3. :ref:`Voronoi diagram calculation`
4. :ref:`Export to GeoJSON`

Weather stations classification
-------------------------------
In order to classify weather stations spatially distributed over a region
into different groups, K-Means algorithm is used. It groups stations by Euclidean
distance and it is implemented in this study using Sci-kit Learn (sklearn_). K-Means
algorithm was chosen for its simplicity and also because it allows to define the
desired resultant number of clusters in which stations are grouped.

An example of the application of this algorithm is shown in :numref:`kmeans_5`.
The automatic weather stations network of the Meteorological Service of Catalonia
are classified in three different groups.

.. figure:: _static/kmeans_5_clusters.png
    :name: kmeans_5
    :width: 650px
    :align: center
    :height: 500px
    :alt: Not available. kmeans_5_clusters.png
    :figclass: align-center

    Plot of the automatic weather stations of Catalonia classified in 5 clusters.

Delaunay triangulation
----------------------
Once the weather stations are classified in different groups a Delaunay triangulation
is performed. The triangulation implies that no point, weather stations in this
case, falls in the circumcircle of any triangle (:numref:`delane_circum`). It is implemented on pyMICA
using d3delaunay_ javascript repository.

.. figure:: _static/delaunay_circumcircles.png
    :name: delane_circum
    :width: 550px
    :align: center
    :height: 400px
    :alt: Not available. kmeans_5_clusters.png
    :figclass: align-center

    Plot of the circumcircles of Delaunay triangulation to randomly distributed points.
    Image taken from `here <https://www.researchgate.net/figure/A-delaunay-triangulation-in-the-plane-with-circumcircles_fig17_267981888>`_

If Delaunay triangulation is applied to a bigger number of spatially distributed
points, the result is shown in :numref:`delane_points`

.. figure:: _static/delaunay_points.png
    :name: delane_points
    :width: 550px
    :align: center
    :height: 400px
    :alt: Not available. kmeans_5_clusters.png
    :figclass: align-center

    Plot of the application of Delaunay triangulation to randomly distributed points.
    Image taken from d3delaunay_.


Voronoi diagram calculation
---------------------------
Once the Delaunay triangulation is performed, Voronoi diagram is calculated. This
diagram connects the circumcentres of adjacent triangles resultant from the 
Delaunay triangulation. It is implemented using the same 
d3delaunay_ repository as the above section.

If Voronoi diagram is applied to :numref:`delane_points` the following is obtained
:numref:`voronoi_points`

.. figure:: _static/voronoi_points.png
    :name: voronoi_points
    :width: 550px
    :align: center
    :height: 400px
    :alt: Not available. kmeans_5_clusters.png
    :figclass: align-center

    Plot of the calculation of Voronoi diagram to :numref:`delane_points`.
    Image taken from d3delaunay_.

Export to GeoJSON
-----------------
The polygons created are exported as GeoJSON format. An example of the 
result obtained using the clustering software can be seen in :numref:`clust_3`

.. figure:: _static/clustering_3.png
    :name: clust_3
    :width: 550px
    :align: center
    :height: 400px
    :alt: Not available. clustering_3.png
    :figclass: align-center

    Screenshot of the browser to edit and export to GeoJSON the automatically
    defined clusters.
