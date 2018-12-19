'''
Calculates the interpolation for a field, using the points data,
the interpolation options and the residuals calculation.
'''
import numpy as np
from interpolation.inverse_distance import inverse_distance
from pymica.apply_regression import apply_regression
from pymica.multiregression import MultiRegression, MultiRegressionSigma


def calculate_field(points_data, raster_data, geotransform, sigma=True):
    """
    Calculates a variable field from the points data and the known
    variables fields.

    Args:
        points_data (list): The point data to create the field calculation.
                            All the needed variables must be here, including:
                            id, y_variable, x_variables, x, y and z positions
        raster_data (np.ndarray): a 3D array with all the x_variables values,
                                  ordered as the x_vars definition
        geotransform (list): The geotransform to translate the points
                             coordinates to raster positions, as explained
                             in the gdal docs:
                             https://www.gdal.org/gdal_datamodel.html
        sigma (bool, optional): Defaults to True. Wether to eliminate or not
                                the values outside the 1.5 sigma value, to
                                improve the interpolation function.

    Returns:
        np.ndarray: The final calculated field
    """

    if isinstance(points_data, list):
        data = points_data
    else:
        pass

    if sigma is True:
        regression = MultiRegressionSigma(data)
    elif isinstance(sigma, float):
        regression = MultiRegressionSigma(data, sigma_limit=sigma)
    else:
        regression = MultiRegression(data)

    regression_field = apply_regression(regression.get_coefs(),
                                        np.array(raster_data))

    residuals = regression.get_residuals()

    interpolation_values = {}
    for point in points_data:
        interpolation_values[point['id']] = {'x': point['x'], 'y': point['y'],
                                             'value': residuals[point['id']]}

    residuals = inverse_distance([interpolation_values,
                                 [raster_data[0].shape[1],
                                  raster_data[1].shape[0]],
                                  geotransform],
                                 )

    return regression_field - residuals
