Interpolation
=============
The MICA software obtains an interpolated field through applying the
regression coefficients to a raster and an anomaly correction. This
correction is obtained interpolation the regression residuals before
adding the field to the interpolation result, which can be done using 
several methods:

- :ref:`Inverse of the distance (2D)`
- :ref:`IDW`


Apply regression
----------------

.. automodule:: pymica.apply_regression
    :members:

Inverse of the distance (2D)
----------------------------

.. automodule:: interpolation.inverse_distance
    :members:

IDW
---

.. automodule:: interpolation.idw
    :members: