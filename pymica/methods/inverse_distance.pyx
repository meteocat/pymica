#cython: boundscheck=False, wraparound=False, nonecheck=False, cdivision=True
"""
A residue value is calculated for a point considering the quadratic inverse
of the distance between the point and all the stations.
"""

import numpy as np
cimport numpy as np
from libc.math cimport sqrt
from libc.math cimport pow
from cpython cimport array
import array
from typing import Dict, List

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

def inverse_distance(data: List[Dict[str, float]],
                     size: List[int], geotransform: List[int],
                     power: int=2, smoothing: float=0.0):
    """
    inverse_distance(data, size, geotransform)

    Interpolates the data field using the inverse of the distance method
    
    Args:
        data (dict): The data dict
        size (list): x X y
        geotransform (list): The geotransform to apply to relate the data coordinates
                             and the position in the matrix.
                             See https://www.gdal.org/gdal_datamodel.html for more information

    Returns:
        list: The interpolated data
    """

    cdef array.array da = array.array('d', [])
    array.resize(da, size[0] * size[1])
    cdef double[:] cda = da

    xpos0 = []
    ypos0 = []
    values0 = []

    for d in data:
        xpos0.append(d['x'])
        ypos0.append(d['y'])
        values0.append(d['value'])

    cdef int N
    N = len(xpos0)
    #http://cython.readthedocs.io/en/latest/src/tutorial/array.html
    cdef array.array xpos = array.array('d', xpos0)
    cdef double[:] cxpos = xpos
    cdef array.array ypos = array.array('d', ypos0)
    cdef double[:] cypos = ypos
    cdef array.array values = array.array('d', values0)
    cdef double[:] cvalues = values

    cdef int i, j
    cdef int xsize = size[1]
    cdef int ysize = size[0]
    cdef double y
    cdef double x

    cdef array.array geotransform0 = array.array('d', geotransform)
    cdef double[:] cgeotransform = geotransform0

    for j in range(ysize):
        y = cgeotransform[3] + j * cgeotransform[5]
        for i in range(xsize):
            x = cgeotransform[0] + i * cgeotransform[1]
            cda[i + j * xsize] = point_residue(x, y, cxpos, cypos, cvalues, N, power, smoothing)

    data_array = np.array(cda)
    return data_array.reshape(size)


cdef inline float point_residue(double x, double y,
                                double[:] xpos, double[:] ypos,
                                double[:] values, int N,
                                int power, float smoothing) nogil:
    cdef double numerator = 0.0
    cdef double denominator = 0.0
    cdef double dx, dy, dist_sq, weight
    cdef int i

    smoothing = smoothing * smoothing  # square once

    for i in range(N):
        dx = x - xpos[i]
        dy = y - ypos[i]
        dist_sq = dx * dx + dy * dy + smoothing

        if dist_sq < 1e-11:
            return values[i]

        if power == 2:
            weight = 1.0 / dist_sq
        else:
            weight = 1.0 / fast_pow(dist_sq, power // 2)

        numerator += values[i] * weight
        denominator += weight

    if denominator != 0.0:
        return numerator / denominator
    return 0.0


cdef inline double fast_pow(double base, int exp) nogil:
    cdef double result = 1.0
    while exp > 0:
        if exp & 1:
            result *= base
        base *= base
        exp >>= 1
    return result