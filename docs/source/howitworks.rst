How MICA works?
===============

.. _SKLearn: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

In this section, the general ideas of how MICA works will be explained
following the next index:

:ref:`1. Pre-processing`

  - :ref:`1.1 Clustering stations`
  - :ref:`1.2 Preparation of explanatory variables`
  	
:ref:`2. Processing`

  - :ref:`2.1 Calculating MLRs and residues`
  - :ref:`2.2 Comparison of 1 cluster and n clusters residues`

:ref:`3. Post-processing`

  - :ref:`3.1 Obtaining interpolated and weight fields`
  - :ref:`3.2 Obtaining the merged field`

1. Pre-processing
-----------------

1.1 Clustering stations
-----------------------
It is a semi-supervised process. First, clustering is performed by the K-Means 
algorithm provided by SciKit-Learn (SKLearn_)
which allows to specify the resultant number of clusters to group stations.
Using this algorithm, a first classification of stations is completely objective
and unsupervised. Then, however, two restrictions are made to the resultant clusters:

- The number of stations per cluster must be at least 20.
- The stations included in a cluster must be representative of the area 
  covered by the cluster. For example, the altitude distribution of the 
  stations included in a cluster must agree with the Digital Elevation Model
  (DEM) altitude distribution of the cluster.

The latter is critical as it prevents unrealistic values to show up. 
For example, a cluster formed by 20 stations placed at an altitude range between 10
and 300 m ASL with a cluster area altitude range of 0-1200 m ASL. In this case,
the station altitude distribution does not represent properly the altitudes of
the cluster and may result in an interpolated field that can not be physically
explained. One way to overcome this situation is to modify the cluster
area by introducing new stations into the cluster until there is an agreement between
the stations altitude and the altitudes of the cluster area. In this case,
stations can be included in two or three clusters at the same time.

1.2 Preparation of explanatory variables
----------------------------------------
All the explanatory variables that are going to be considered for the MLR
(:ref:`Multiple Linear Regression`) must be defined. In this case,
altitude raster is built using a DEM with a spatial resolution of 270 m.
The rest of the explanatory variables must be prepared in accordance with
the spatial resolution and extent of the altitude raster.

2. Processing
-------------

2.1 Calculating MLRs and residues
---------------------------------
First, a MLR is calculated using all the stations available. Four explanatory
variables are considered: altitude, latitude, longitude and distance to coast.
Then, the regression residues are obtained. Since the MLR calculation includes
all the stations, henceforward is referred to global MLR and therefore 
global residues.

Since there are different numbers of clusters, each of them are considered
separately. A MLR is calculated for each cluster (internal division) of each number of
clusters contemplated, hereafter cluster MLR. This, is performed taking into account the stations
that fall inside the cluster. For every cluster the residues are also obtained.
In Table 1 there is an example of the calculations involved in dividing an
AWS network in three different numbers of clusters.

Table 1. Example of 1, 2 and 3 clusters and corresponding Cluster IDs and MLR and
residues calculations.

+---------------+------------+--------------------+
| # of clusters | Cluster ID | MLR & Residues     |
+===============+============+====================+
| 1             | 1          | [x]                |
+---------------+------------+--------------------+
| 2             | 2.1        | [x]                |
+---------------+------------+--------------------+
|               | 2.2        | [x]                |
+---------------+------------+--------------------+
| 3             | 3.1        | [x]                |
+---------------+------------+--------------------+
|               | 3.2        | [x]                |
+---------------+------------+--------------------+
|               | 3.3        | [x]                |
+---------------+------------+--------------------+

2.2 Comparison of 1 cluster and n clusters residues
---------------------------------------------------
The global methodology considers one MLR, so a unique RMSE
is obtained. On the other hand, an RMSE is obtained for each numbers
of clusters considered, but obtained comparing the RMSE of each 
internal division with the global methodology. This comparison is done
following the next steps:

1. Obtaining RMSE for a cluster considering the cluster MLR (RMSE :math:`_{Cluster}`). 
2. Obtaining RMSE for a cluster considering the global MLR (RMSE :math:`_{Global}`).
3. Once the two values are obtained two situations may occur:

   a. If RMSE :math:`_{Cluster}` < RMSE :math:`_{Global}`, the MLR for that cluster
      is selected as it improves the MLR global.
   b. If RMSE :math:`_{Cluster}` >= RMSE :math:`_{Global}`, the MLR for all the
      stations is selected as the MLR for the cluster does not improve the current error.	

This process is repeated for every cluster of a number of clusters. 
This means that each cluster RMSE is compared against the global RMSE calculated 
with the same stations included in the cluster. The combination that results in a
lower RMSE is selected for each number of clusters. See the example in Table 2.

Table 2. Example of 1, 2 and 3 clusters and corresponding RMSEs.

+---------------+------------+---------------+------------------------------+-----------------------------+----------------------------+
| # of clusters | Cluster ID | # of stations | RMSE :math:`_{Cluster}` (°C) | RMSE :math:`_{Global}` (°C) | RMSE :math:`_{Final}` (°C) |
+===============+============+===============+==============================+=============================+============================+
| 1             | 1.1        | 120           | 1.5                          | 1.5                         | 1.5                        |
+---------------+------------+---------------+------------------------------+-----------------------------+----------------------------+
| 2             | 2.1        | 60            | 1.2 [x]                      | 2.0                         | 1.1                        |
+---------------+------------+---------------+------------------------------+-----------------------------+----------------------------+
|               | 2.2        | 60            | 1.2                          | 1.0 [x]                     |                            |
+---------------+------------+---------------+------------------------------+-----------------------------+----------------------------+
| 3             | 3.1        | 40            | 1.2 [x]                      | 1.8                         | 1.2                        |
+---------------+------------+---------------+------------------------------+-----------------------------+----------------------------+
|               | 3.2        | 40            | 1.2 [x]                      | 1.5                         |                            |
+---------------+------------+---------------+------------------------------+-----------------------------+----------------------------+
|               | 3.3        | 40            | 2.1                          | 1.3 [x]                     |                            |
+---------------+------------+---------------+------------------------------+-----------------------------+----------------------------+

In Table 2 three number of clusters are contemplated: 1, 2, 3. Firstly, only one
cluster is considered (global) and the RMSE is 1.5°C.
Secondly, the AWS network is divided in two clusters. Two RMSE are compared for
Cluster 2.1: the first one (RMSE :math:`_{Cluster}`) is obtained considering the 
residues obtained by the MLR :math:`_{Cluster}` calculated using the stations included
in the cluster. The second one (RMSE :math:`_{Global}`) is obtained considering the residues
of the stations that fall inside the cluster but with the MLR :math:`_{Global}`,
calculated using all stations. In this case, MLR :math:`_{Cluster}` performs
better than MLR :math:`_{Global}` because the RMSE :math:`_{Cluster}` is lower, so the
MLR :math:`_{Cluster}` for Cluster 2.1 is kept. On the contrary, for Cluster 2.2 the
RMSE :math:`_{Global}` is lower than RMSE :math:`_{Cluster}`, so the MLR :math:`_{Global}` 
will be kept for that cluster. The initial error was 1.5°C (Cluster 1.1),
but now the error is reduced to 1.1°C. 

This example is useful to show that not every MLR :math:`_{Cluster}` perform always better
than the MLR :math:`_{Global}` and that the MICA system will only keep the MLR :math:`_{Cluster}`
that improves the existing one. In this case, the combination of the MLR :math:`_{Cluster}`
for Cluster 2.1 and the MLR :math:`_{Global}` for Cluster 2.2 is the one that, in terms
of RMSE, performs the best. A similar result is obtained when considering three clusters:
two MLR :math:`_{Cluster}` are selected for Clusters 3.1 and 3.2 and a MLR :math:`_{Global}`
for Cluster 3.3. The RMSE outcome for this combination is 1.2°C. 
Although it is 0.3°C better than 1 cluster performance, is 0.1°C 
worse than using only two cluster. In this case, the two cluster option is selected as it results
in the lowest final RMSE among the three options available.

3. Post-processing
------------------

3.1 Obtaining interpolated and weight fields
--------------------------------------------

This part of the system receives the parameters of the MLRs of the number of 
clusters selected in the previous section. In this case and following the above
example, the MLRs selected are:

Table 3. MLR parameters for each cluster for the number of clusters selected.

+------------------------+------------+------------------------+
| # of clusters selected | Cluster ID | MLR coefficients       |
+========================+============+========================+
| 2                      | 2.1        | MLR :math:`_{Cluster}` |
+------------------------+------------+------------------------+
|                        | 2.2        | MLR :math:`_{Global}`  |
+------------------------+------------+------------------------+

The following procedure is done for every cluster selected:

1. An interpolated field for the whole extension, country or region, is obtained 
   using the MLR coefficients and the anomaly correction of the residuals is applied.
2. The cluster polygon associated with the MLR used is rasterized. The polygon
   becomes a raster with value 1 inside the polygon and 0 outside of it. Then 
   the raster is blurred. The blurring effect allows to smooth the boundary of
   the raster from 1 to 0 progressively rather than sharply. Then, a sharp
   transition with adjacent clusters is avoided. This raster will be used for
   the final temperature field and from now on will be labelled as 'weight'
   field (W).
3. The interpolated field from 1 is multiplied by the rasterized and blurred
   polygon (weight) from 2.

The resultant fields of the previous process are shown in Table 4.

Table 4. Resultant fields for each cluster for the selected number of clusters.

+------------------------+------------+-------------------------------------------+
| # of clusters selected | Cluster ID | Field                                     |
+========================+============+===========================================+
| 2                      | 2.1        | T :math:`_{2.1}` field                    |
+------------------------+------------+-------------------------------------------+
|                        | 2.1        | W :math:`_{2.1}` field                    |
+------------------------+------------+-------------------------------------------+
|                        | 2.1        | T :math:`_{2.1}` · W :math:`_{2.1}` field |
+------------------------+------------+-------------------------------------------+
|                        | 2.2        | T :math:`_{2.2}` field                    |
+------------------------+------------+-------------------------------------------+
|                        | 2.2        | W :math:`_{2.2}` field                    |
+------------------------+------------+-------------------------------------------+
|                        | 2.2        | T :math:`_{2.2}` · W :math:`_{2.2}` field |
+------------------------+------------+-------------------------------------------+

3.2 Obtaining the merged field
------------------------------

Considering the fields of Table 4, the final temperature field can be obtained with 
the following equation.

.. math::
    
    T_{Final} = \dfrac{T_{2.1} · W_{2.1} + T_{2.2} · W_{2.2}}{W_{2.1}+W_{2.2}}
