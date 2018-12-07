'''
Once the regression coefficients are calculated, this function applies them
to a raster.
'''
import numpy as np


def apply_regression(coefs, raster_data):
    """Apply the regression coefficients to a raster to obtain the interpolated
    field.
    
    Args:
        coefs (list): List of the regression coefficients and the intercept
        raster_data (np.ndarray): a 3D array with all the x_variables values,
                                  ordered as the x_vars definition
    
    Raises:
        ValueError: If raster data is not a 3 dimensional array 
    
    Returns:
        np.ndarray: Interpolated field without residuals correction
    """

    if not type(raster_data) == np.ndarray or len(raster_data.shape) != 3:
        raise ValueError("raster_data must be a 3 dimensional array")
    out_data = coefs[1] * np.ones((raster_data[0].shape[0],
                                   raster_data[0].shape[1]))

    for k in range(len(coefs[0])):
        out_data += coefs[0][k] * raster_data[k]

    return out_data