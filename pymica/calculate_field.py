'''Calculates the interpolation for a field, using the points data,
the interpolation options and the residuals calculation
'''
from pymica.multiregression import MultiRegression
from pymica.multiregression import MultiRegressionSigma


def calculate_field(points_data, raster_data, sigma=True):
    if type(points_data) == list:
        data = points_data
    else:
        pass

    if sigma is True:
        regression = MultiRegressionSigma(data)
    elif type(sigma) is float:
        regression = MultiRegressionSigma(data, sigma_limit=sigma)
    else:
        regression = MultiRegression(data)

    return regression
