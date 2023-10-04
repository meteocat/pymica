Multiple Linear Regression
==========================

Multiple Linear Regression (MLR) allows for the prediction of a response
variable using different explanatory variables, as opposed to only one in
simple linear regressions. It can be expressed as:

.. math::

    y_{i} = \sum_{k}^{} \beta_{k}x_{ik} + \epsilon_{i}

Where:

- :math:`y_{i}` is the predictand.
- :math:`\beta_{k}` are the coefficients of linear regression.
- :math:`x_{ik}` are the predictors.
- :math:`\epsilon_{i}` are the residues of the regression, which represent the difference between the predicted and observed values.

In the case of MLR, the predictors are included in a forward stepwise process.
First, the correlation coefficient is tested for each predictor. The one that
correlates the best is selected and left out for the next step. Second, each
of the remaining predictors is added to the previous regression. If the correlation
coefficient combining the first predictor and the second one improves by at least a
threshold of 0.05, a second predictor is considered. The one that improves the
correlation coefficient the most is selected. This process is repeated until the
improvement of adding one predictor is less than the established threshold or there
are no more predictors available.


Explanatory Variables
---------------------

The explanatory variables or predictors are those considered for predicting a
response variable. In this study, the selected explanatory variables include altitude,
longitude, latitude, and distance to the coast.

Altitude can be derived from a Digital Elevation Model (DEM). For the Catalonia study case,
a 250-meter resolution DEM was chosen. Longitude, latitude, and distance to the coast are defined
based on the resolution and extent of the selected DEM. However, the distance to the coast is
calculated using a logarithmic function rather than the Euclidean distance itself
and can be expressed as:

.. math::

    d_{sea} = 1 - e^{-\dfrac{3 \times \text{dist}}{D}}

Where:

- :math:`d_{sea}` is the resultant distance to the coast based on the function.
- *dist* is the Euclidean distance from a point to the coastline.
- *D* is the distance at which the distance to the coast becomes negligible.

A plot of this function is shown in Figure :numref:`dsea_function` with *D* = 100 kilometers.

.. figure:: _static/dsea_function.png
    :name: dsea_function
    :width: 500px
    :align: center
    :height: 400px
    :alt: Distance to sea plot
    :figclass: align-center

    Plot of the distance to the coast function with *D* = 100 km.

This function has a value of 0 at the coastline and approaches 1 as the Euclidean
distance (*dist*) increases beyond a certain threshold (*D*). Thus, stations closer
to the sea receive a higher weight, while those farther from the coastline have the
same :math:`d_{sea}` value, as differences in sea influence become negligible.
An example of the :math:`d_{sea}` function applied to a map is shown in
Figure :numref:`dsea_map`.

.. figure:: _static/dsea_function_map.png
    :name: dsea_map
    :width: 600px
    :align: center
    :height: 500px
    :alt: Distance to sea map
    :figclass: align-center

    Map of Catalonia showing the corresponding distance to the coast function. *D* = 100 km.
