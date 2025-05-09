#cython: boundscheck=False, wraparound=False, nonecheck=False, cdivision=True
"""
A residue value is calculated for a point considering not only the distance 
between the point and all the stations, but also their altitude difference. 
"""

import numpy as np
cimport numpy as np
from libc.math cimport sqrt
from libc.math cimport pow
from cpython cimport array
import array
from typing import Dict, List, Union

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

def inverse_distance_3d(data: List[Dict[str, float]],
                        size: List[int], geotransform: List[int], dem,
                        int power=2, int smoothing=0,
                        int penalization=30):
    """
    inverse_distance_3d(residues, size, geotransform, dem)

    Interpolates the residues field using the inverse of the distance method
    
    Args:
        residues (dict): The residues dict
        size (list): x X y
        geotransform (list): The geotransform to apply to relate the residues coordinates
                             and the position in the matrix.
                             See https://www.gdal.org/gdal_datamodel.html for more information
        dem(np.array): 2-D array of altitudes with the same geotransform
    
    Returns:
        list: The interpolated residues
    """

    cdef array.array da = array.array('d', [])
    array.resize(da, size[0] * size[1])
    cdef double[:] cda = da

    xpos0 = []
    ypos0 = []
    zpos0 = []
    values0 = []

    for d in data:
        xpos0.append(d['x'])
        ypos0.append(d['y'])
        zpos0.append(d['altitude'])
        values0.append(d['value'])

    cdef int N
    N = len(xpos0)
    #http://cython.readthedocs.io/en/latest/src/tutorial/array.html
    cdef array.array xpos = array.array('d', xpos0)
    cdef double[:] cxpos = xpos
    cdef array.array ypos = array.array('d', ypos0)
    cdef double[:] cypos = ypos
    cdef array.array zpos = array.array('d', zpos0)
    cdef double[:] czpos = zpos
    cdef array.array values = array.array('d', values0)
    cdef double[:] cvalues = values

    cdef int i, j
    cdef int xsize = size[1]
    cdef int ysize = size[0]
    cdef double y
    cdef double x
    cdef double z

    cdef array.array geotransform0 = array.array('d', geotransform)
    cdef double[:] cgeotransform = geotransform0

    for j in range(ysize):
        y = cgeotransform[3] + j * cgeotransform[5]
        for i in range(xsize):
            x = cgeotransform[0] + i * cgeotransform[1]
            z = dem[j, i]
            cda[i + j * xsize] = point_residue(x, y, z, cxpos, cypos, czpos,
                                               cvalues, N, power, smoothing,
                                               penalization)

    data_array = np.array(cda)
    return data_array.reshape(size)

cdef float point_residue(double x, double y, double z,
                               double[:] xpos, double[:] ypos,
                               double[:] zpos, double[:] values, int N,
                               int power, int smoothing, int penalization):
    cdef double numerator = 0
    cdef double denominator = 0
    cdef double dist, dist_3d, dist3d_sq, weight
    cdef int i

    for i in range(N):
        dist = sqrt((x - xpos[i]) * (x - xpos[i]) +
                    (y - ypos[i]) * (y - ypos[i]))

        if dist < 1e-11:
            return values[i]

        dist3d_sq = dist * dist + (penalization * (z - zpos[i])) ** 2 + smoothing * smoothing

        if power == 2:
            weight = 1.0 / dist3d_sq
        elif power == 3:
            weight = 1.0 / (dist3d_sq * sqrt(dist3d_sq))  # faster than full pow
        else:
            weight = 1.0 / fast_pow(dist3d_sq, power // 2)

        numerator += values[i] * weight
        denominator += weight

    if denominator != 0:
        return numerator / denominator
    return 0


cdef inline double fast_pow(double base, int exp) nogil:
    cdef double result = 1.0
    while exp > 0:
        if exp % 2 == 1:
            result *= base
        base *= base
        exp //= 2
    return result