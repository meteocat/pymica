'''
Once the regression coefficients are calculated, this function applies them
to a raster.
'''
import numpy as np

def apply_regression(coefs, raster_data):

    out_data = np.ones((out_config['size'][1], out_config['size'][0])) * coefs[1]

    for k in range(len(coefs[0])):
        out_data += coefs[0][k] * in_data[k]

    return out_data