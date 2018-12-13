'''Interpolate residuals, methodology choice
'''
from interpolation.inverse_distance import inverse_distance
from interpolation.inverse_distance_3d import inverse_distance_3d
from interpolation.idw import Tree


def interpolate_residuals(data, methodology):
    '''Interpolates residuals following the indicated methodology

    Args:
        data (list): list of required data to interpolate residuals (residuals,
                     size, geotransform)
        methodology (string): indicates the methodology to follow to
                              interpolate the residuals
                              Options:
                                id2d = inverse of the 2D distance
                                id3d = inverse of the 3D distance
                                idw  = inverse of the distance weighting

    Returns:
        np.ndarray: The interpolated residual field
    '''

    if methodology is 'id2d':
        residuals = inverse_distance(data[0], data[1], data[2])
    elif methodology is 'id3d':
        residuals = inverse_distance_3d(data[0], data[1], data[2])
    elif methodology is 'idw':
        inst_tree = Tree()
        residuals = inst_tree(data[0], data[1], data[2])
    else:
        raise ValueError("Residuals interpolation methodology indicator must" +
                         "be a string like id2d, id3d or idw")

    return residuals
