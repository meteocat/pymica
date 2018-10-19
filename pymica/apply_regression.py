'''
Once the regression coefficients are calculated, this function applies them
to a raster
'''
import numpy as np


def apply_regression(coefs, raster_data):

    if not type(raster_data) == np.ndarray or len(raster_data.shape) != 3:
        raise ValueError("raster_data must be a 3 dimensional array")
    out_data = coefs[1] * np.ones((raster_data[0].shape[0],
                                   raster_data[0].shape[1]))

    for k in range(len(coefs[0])):
        out_data += coefs[0][k] * raster_data[k]

    return out_data