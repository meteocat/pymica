How MICA works?
===============

.. _SKLearn: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

In this section, the general ideas of how MICA works will be explained
following the next index:

:ref:`1. Starting point`

  - :ref:`Calculating MLR considering all stations`
  - :ref:`Computing residues of MLR`
  - :ref:`Obtaining statistics`
	
:ref:`2. Clustering`

  - :ref:`Grouping stations`
  - :ref:`Calculating MLRs for each cluster`
  - :ref:`Computing residues for each cluster`
  - :ref:`Obtaining statistics for each number of clusters`
	
:ref:`3. 1 cluster vs n clusters`
    
:ref:`4. Merging`

  - :ref:`Obtaining interpolated and weight fields`
  - :ref:`Obtaining the merged field`

1. Starting point
-----------------

Calculating MLR considering all stations
----------------------------------------
A MLR is calculated using all stations available in the AWS network.
Four explanatory variables are considered: altitude, latitude, longitude
and distance to coast. The later consists of a logarithmic function
which cancels the sea influence around 100 km from the coast line.
The MLR parameters are used to obtain a preliminary field of the
meterological variable of interest (from now on, temperature).

Computing residues of MLR
-------------------------
The residues are the difference between a predicted value, in this
case by the MLR, and an observed value. For each weather station a
residue is obtained. The residues are interpolated and an anomaly
field is computed. The MICA system offers the possibility to get the
residues field through different interpolation methodologies: 2D
inverse of the distance, 3D inverse of the distance, inverse of the
distance weighted (IDW) and 3D Ordinary Kriging. 

The residues field is subtracted from the above-mentioned preliminary 
temperature field, this way predicted values are corrected at observation
locations.

Obtaining statistics
--------------------
Once the residues are calculated, several statistic parameters are
calculated to evaluate the regression performance: RMSE, MAE and BIAS.

2. Clustering
-------------

Grouping stations
-----------------
Defining clusters allows to classify AWS in different regions that
can be more climatically consistent than considering only one group
including all the stations. The latter is the starting point of this
study which can be labelled as '1 cluster', since no groups are 
contemplated. 

One of the main ideas of the MICA system is to not to fix a number of 
clusters, but to be dynamically chosen in terms of they performance. 
For example, SMC's AWS network is formed by 183 stations and they can 
be divided in 2, 3, 4, ... , up to 183 clusters. 

Clustering is performed by the K-Means algorithm provided by SciKit-Learn (SKLearn_)
which allows to specify the resultant number of clusters to group stations.
Using this algorithm, a first classification of stations is completely objective
and unsupervised. However, two restrictions are made to the resultant clusters:

- The number of stations per cluster must be at least 15.
- The stations included in a cluster must be representative of the area 
  covered by the cluster. For example, the altitude distribution of the 
  stations included in a cluster must agree with the Digital Elevation Model
  (DEM) altitude distribution of the cluster.

The latter is very important as it prevents unrealistic values to show up. 
For example, a cluster formed by 15 stations placed at an altitude range between 10
and 300 m ASL with a cluster area altitude range of 0-1200 m ASL. In this case,
the station altitude distribution does not represent properly the altitudes of
the cluster and may result in an interpolated field that can not be physically
explained. One way to overcome this situation is to modify the cluster
area by introducing new stations into the cluster until there is an agreement between
the stations altitude and the altitudes of the cluster area. In this case,
stations can be included in two or three clusters at the same time.

As the clustering algorithm used does not account for the two restrictions imposed,
the resultant station groups must be carefully analysed. For this reason, pyMICA
provides a tool to evaluate the altitude distribution of the stations included in
a cluster and the altitude distribution of the area covered by the cluster.

Calculating MLRs for each cluster
---------------------------------
The starting point is one cluster and one MLR calculation. As MICA system works 
with different number of clusters, there will be as many MLR calculations as clusters.
For example, if the AWS network is divided in 3 clusters, there will be three MLR calculations.
There is not a pre defined number of clusters, so imagine that an AWS network is
divided in 1, 2 and 3 clusters. The total number of MLR to calculate is 6 as it is shown 
in Table 1. Each MLR is calculated considering the stations included in each cluster
and their altitude, distance to the sea, latitude and longitude as explanatory variables.

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

Computing residues for each cluster
-----------------------------------
Following the previous example, residues are calculated six times, one for each
resultant cluster of the three different number of clusters considered (Table 1).
It is possible that some clusters of the same number of clusters share the same station.
In this case, station residue would be calculated twice and both residues may not be the
same. However, this does not affect the quality of the interpolation as in both cases
the value at the station location will be the same due to the residual correction.

Obtaining statistics for each number of clusters
------------------------------------------------
Once the residues are calculated for the clusters of the different number of
clusters considered, several statistic parameters are calculated to evaluate
the regression performance. RMSE, MAE and BIAS are obtained.

3. 1 cluster vs n clusters
--------------------------
The 1 cluster methodology considers one MLR, so a unique RMSE for all stations
is obtained. The comparison between 1 cluster RMSE and the different RMSEs calculated
for n clusters is not done at a global scale but cluster by cluster following
the next steps:

1. Obtain RMSE for the cluster considering the MLR for that cluster (RMSE :math:`_{Cluster}`). 
2. Obtain RMSE for the cluster considering the MLR for all the stations (RMSE :math:`_{Global}`).
3. Once the two values are obtained two situations may occur:

   a. If RMSE :math:`_{Cluster}` < RMSE :math:`_{Global}`, the MLR for that cluster
      is selected as it improves the MLR global.
   b. If RMSE :math:`_{Cluster}` > RMSE :math:`_{Global}`, the MLR for all the
      stations is selected as the MLR for the cluster does not improve the current error.	

This process is repeated for every cluster. This means that each cluster RMSE is
compared against the global RMSE for the same stations included in the cluster.
The combination that results in a lower RMSE is selected for each number of clusters.
See the example in Table 2.

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
cluster is considered (all stations included in a cluster) and the RMSE is 1.5°C.
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

4. Merging
----------

Obtaining interpolated and weight fields
----------------------------------------
This part of the system receives the parameters of the MLRs of the number of clusters selected
in the previous section. In this case and following the above example, the MLRs selected are:

Table 3. MLR parameters for each cluster for the number of clusters selected.

+------------------------+------------+------------------------+
| # of clusters selected | Cluster ID | MLR parameters         |
+========================+============+========================+
| 2                      | 2.1        | MLR :math:`_{Cluster}` |
+------------------------+------------+------------------------+
|                        | 2.2        | MLR :math:`_{Global}`  |
+------------------------+------------+------------------------+

The following procedure is done for every cluster selected:

1. An interpolated field for the whole extension, country or region, is obtained 
   using the MLR parameters.
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

Obtaining the merged field
--------------------------
Considering the fields of Table 4, the final temperature field can be obtained with 
the following equation.

.. math::
    
    T_{Final} = \dfrac{T_{2.1} · W_{2.1} + T_{2.2} · W_{2.2}}{W_{2.1}+W_{2.2}}
