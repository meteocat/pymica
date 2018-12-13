'''
Once the regression coefficients are calculated, this function applies them
to a raster.
'''
import numpy as np


def apply_regression(regr, raster_data, raster_fields):
    '''Applies the regression formula to an array, to
    get all the values for each point

    Args:
        regr (MultiRegression): A MultiRegression or MultiRegressionSigma
                                instance
        raster_data (nd.array): A three dimension array with the values to
                                apply
        raster_fields (list): The variable names as passed into MultiRegression
                              and in the order they appear in raster_data.
                              Used to apply the fields in the correct order.

    Raises:
        ValueError: The array has wrong dimensions

    Returns:
        nd.array: A 2-D array with all the calculated values
    '''
    if not type(raster_data) == np.ndarray or len(raster_data.shape) != 3:
        raise ValueError("raster_data must be a 3 dimensional array")
    coefs = regr.get_coefs()
    out_data = coefs[1] * np.ones((raster_data[0].shape[0],
                                   raster_data[0].shape[1]))

    for i, coef in enumerate(coefs[0]):
        field_pos = raster_fields.index(regr.used_vars[i])
        out_data += coef * raster_data[field_pos]

    return out_data


def apply_clustered_regression(regressions, raster_data, raster_fields, mask):
    '''The same as apply_regression, but using a "clustered regresion".
    The result is weighed by a mask array.

    Args:
        regressions (ClusteredRegression): The ClusteredRegression instance
        raster_data (nd.array): A three dimension array with the values to
                                apply
        raster_fields (list): The variable names as passed into MultiRegression
                              and in the order they appear in raster_data.
                              Used to apply the fields in the correct order.
        mask (nd.array): An array with the zones valid for the cluster with
                         value 1 and the others with value 0.
                         Intermediate values are allowed to overlap zones.
                         Use *create_clusters_file* to generate the data.

    Returns:
       nd.array: The final value array, after overlapping all the clusters.
    '''

    result = np.zeros((mask.shape[1], mask.shape[2]), dtype=np.float64)
    for i, regr in enumerate(regressions.final_regr):
        result += apply_regression(regr, raster_data, raster_fields) * mask[i]

    return result / mask.sum(axis=0)
