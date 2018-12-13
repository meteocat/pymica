"""
Inverse distance weighting (IDW)

Compute the score of query points based on the scores of their k-nearest
neighbours, weighted by the inverse of their distances.

For more information, see :ref:`Inverse of the distance weighting - IDW`

Credits:
https://en.wikipedia.org/wiki/Inverse_distance_weighting
"""

import numpy as np
from scipy.spatial import cKDTree


class Tree(object):
    """
    Compute the score of query points based on the scores of their k-nearest
    neighbours, weighted by the inverse of their distances.
    """

    def __init__(self, coordinates=None, scores=None, leafsize=10):
        """
        Args:
            coordinates (ndarray, optional): Defaults to None.
                                             Coordinates of N sample points
                                             in a d-dimensional space.
            scores (ndarray, optional): Defaults to None.
                                        Corresponding scores.
            leafsize (int, optional): Defaults to 10.
                                      Leafsize of KD-tree data structure;
                                      should be less than 20.
        """

        if coordinates is not None:
            self.tree = cKDTree(coordinates, leafsize=leafsize)
        if scores is not None:
            self.scores = scores

    def fit(self, coordinates=None, scores=None, leafsize=10):
        """Instantiate KDtree for fast query of k-nearest neighbour distances.

        Args:
            coordinates ((N, d) ndarray, optional): Defaults to None.
                         Coordinates of N sample points in a d-dimensional
                         space.
            scores ((N,) ndarray, optional): Defaults to None. Corresponding
                                             scores.
            leafsize (int, optional): Defaults to 10.
                                      Leafsize of KD-tree data structure;
                                      should be less than 20.

        Returns:
            object: idw_tree instance

            """
        return self.__init__(coordinates, scores, leafsize)

    def __call__(self, coordinates, num_nearest=6, eps=1e-6, p_norm=2,
                 regularize_by=1e-9):
        """
        Compute the score of query points based on the scores of their
        k-nearest neighbours, weighted by the inverse of their distances.

        Args:
            coordinates ((N, d) ndarray):
                Coordinates of N query points in a d-dimensional space.
            num_nearest (int): Default to 6
                Number of nearest neighbours to use.
            p_norm (int or inf):
                Which Minkowski p-norm to use.
                1 is the sum-of-absolute-values "Manhattan" distance
                2 is the usual Euclidean distance
                infinity is the maximum-coordinate-difference distance
            eps (float): Defaults to 1e-6
                Return approximate nearest neighbors; the k-th returned value
                is guaranteed to be no further than (1+eps) times the
                distance to the real k-th nearest neighbor.
            regularize_by (float): (default 1e-9)
                Regularize distances to prevent division by zero
                for sample points with the same location as query points.

        Returns:
            (N,) ndarray: Corresponding scores.
        """
        distances, idx = self.tree.query(coordinates, num_nearest,
                                         eps=eps, p=p_norm)
        distances += regularize_by
        weights = self.scores[idx.ravel()].reshape(idx.shape)
        m_w = np.sum(weights/distances, axis=1) / np.sum(1./distances,
                                                         axis=1)
        return m_w

    def transform(self, coordinates, num_nearest=6,
                  p_norm=2, eps=1e-6, regularize_by=1e-9):
        """Compute the score of query points based on the scores of their
        k-nearest neighbours, weighted by the inverse of their distances.

        Args:
            coordinates ((N, d) ndarray):
                Coordinates of N query points in a d-dimensional space.
            num_nearest (int): Defaults to 6
                Number of nearest neighbours to use.
            p_norm (int or inf):
                Which Minkowski p-norm to use.
                1 is the sum-of-absolute-values "Manhattan" distance
                2 is the usual Euclidean distance
                infinity is the maximum-coordinate-difference distance
            eps (float): Defaults to 1e-6
                Return approximate nearest neighbors; the k-th returned value
                is guaranteed to be no further than (1+eps) times the
                distance to the real k-th nearest neighbor.
            regularize_by (float): Defaults to 1e-9
                Regularize distances to prevent division by zero
                for sample points with the same location as query points.
        Returns:
            (N,) ndarray: Corresponding scores.

        """
        return self.__call__(coordinates, num_nearest, eps,
                             p_norm, regularize_by)

    def idw(self, residues, size, geotransform, num_nearest=6):
        '''Interpolates the residues field using the inverse of the distance
           weighting method

        Args:
            residues (dict): The residues dict
            size (list): x X y
            geotransform (list): The geotransform to apply to relate the
                                 residues coordinates and the position in
                                 the matrix.
                                 See https://www.gdal.org/gdal_datamodel.html
                                 for more information
        Returns:
            list: The interpolated residues

        '''
        coords = []
        values = []
        for key in residues.keys():
            coords.append([residues[key]['x'], residues[key]['y']])
            values.append(residues[key]['value'])
        coords = np.array(coords)
        values = np.array(values)

        idw_tree = Tree(coords, values)

        x_coords = np.arange(geotransform[0],
                             geotransform[0]+size[1]*geotransform[1],
                             geotransform[1])

        y_coords = np.arange(geotransform[3],
                             geotransform[3]+size[0]*geotransform[5],
                             geotransform[5])

        xy_coords = np.meshgrid(x_coords, y_coords)
        xy_coords = np.reshape(xy_coords, (2, -1)).T

        idw_array = idw_tree(xy_coords, num_nearest)
        idw_array = idw_array.reshape(size)

        return idw_array
