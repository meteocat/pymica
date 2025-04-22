"""Runs multiple regressions clustering the data in all the ways is asked for
and takes the best option for each zone
"""

import sys
from copy import deepcopy

import numpy as np
from osgeo import ogr, osr

from pymica.methods.multiregression import MultiRegressionSigma


class ClusteredRegression:
    """Calculates multiple linear regressions looking which cluster is better"""

    def __init__(self, data, clusters_files, x_vars, regression_params=None):
        if regression_params is None:
            self.regression_params = {"sigma_limit": 1.5, "score_threshold": 0.05}
        else:
            self.regression_params = regression_params

        regr_all = MultiRegressionSigma(data, x_vars)
        residuals_all = regr_all.get_residuals()

        # Workaround for cases when different clusters share the same
        # station. The mse calculated as
        #       self.mse = __get_residuals_mse__(residuals_all),
        # does not correspond to the mse when stations are in more
        # than one cluster.
        self.mse = sys.float_info.max

        self.final_regr = [regr_all]
        self.final_data = [data]
        self.final_cluster_file = None
        self.x_vars = x_vars

        try:
            for cluster_file in clusters_files:
                cluster_file_regressions = []
                file_mse = 0
                data_used = 0
                clustered_data = __filter_data_by_cluster__(data, cluster_file)
                for data_in_cluster in clustered_data:
                    mse_all = __get_cluster_mse__(residuals_all, data_in_cluster)

                    try:
                        cluster_regression = MultiRegressionSigma(
                            data_in_cluster, x_vars=x_vars
                        )
                        mse_cluster = __get_residuals_mse__(
                            cluster_regression.get_residuals()
                        )
                    except ValueError:
                        mse_cluster = sys.float_info.max

                    if mse_all > mse_cluster:
                        cluster_file_regressions.append(cluster_regression)
                        file_mse += mse_cluster * len(data_in_cluster)
                    else:
                        new_regr_all = deepcopy(regr_all)
                        new_regr_all.original_data = data_in_cluster
                        cluster_file_regressions.append(new_regr_all)
                        file_mse += mse_all * len(data_in_cluster)

                    # Variable to deal with stations present in more than
                    # one cluster
                    data_used = data_used + len(data_in_cluster)

                file_mse = file_mse / data_used
                if file_mse <= self.mse:
                    self.final_regr = cluster_file_regressions
                    self.final_data = clustered_data
                    self.final_cluster_file = cluster_file
                    self.mse = file_mse
        except TypeError as err:
            raise TypeError("cluster file must be a list") from err

    def get_residuals(self):
        """Gets the residuals for each point, using the cluster regresion

        Returns:
            dict: The residuals with the id of the point as a key
        """

        out = {}
        for regr in self.final_regr:
            out.update(regr.get_residuals())
        return out

    def predict_points(self, x_data):
        """Returns the predicted values for multiple points given the
           x variables (predictors). The formula applied will depend on
           the cluster where the point is located, so the method classifies
           the points into the different clusters too.

        Args:
            x_data list: the x variable values list
                                             with the var names as the keys

        Returns:
            list: The predicted values
        """

        clustered_data = __filter_data_by_cluster__(x_data, self.final_cluster_file)
        out = [None] * len(x_data)
        x_data_idx = {}
        for i, data in enumerate(x_data):
            x_data_idx[data["id"]] = i

        for i, cluster_data in enumerate(clustered_data):
            if cluster_data:
                result = self.final_regr[i].predict_points(cluster_data)
                for data in zip(cluster_data, result):
                    out[x_data_idx[data[0]["id"]]] = data[1]
        return out

    def apply_clustered_regression(self, raster_data, raster_fields, mask):
        """The same as apply_regression, but using a "clustered regresion".
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
        """

        result = np.zeros((mask.shape[1], mask.shape[2]), dtype=np.float64)
        for i, regr in enumerate(self.final_regr):
            result += __apply_regression__(regr, raster_data, raster_fields) * mask[i]

        return result / mask.sum(axis=0)


def __filter_data_by_cluster__(data, cluster):
    ds_in = ogr.Open(cluster)
    if not ds_in:
        raise FileNotFoundError(
            "File not found, or not ogr compatible {}".format(cluster)
        )
    layer = ds_in.GetLayer()
    num_clusters = layer.GetFeatureCount()
    classified_data = []
    for _ in range(num_clusters):
        cluster_points = []
        feat = layer.GetNextFeature()
        cluster_geom = feat.GetGeometryRef()

        input_srs = osr.SpatialReference()
        input_srs.ImportFromEPSG(4326)
        cluster_srs = cluster_geom.GetSpatialReference()
        transform = osr.CoordinateTransformation(input_srs, cluster_srs)

        for point in data:
            point_geom = ogr.Geometry(ogr.wkbPoint)
            # Transform lon lat coordinates to cluster projection
            point_geom.AddPoint(point["lat"], point["lon"])
            point_geom.Transform(transform)
            if point_geom.Within(cluster_geom):
                cluster_points.append(point)
        classified_data.append(cluster_points)

    return classified_data


def __get_residuals_mse__(residuals):
    mse = 0
    for i in residuals:
        mse += residuals[i] ** 2

    return mse / len(residuals)


def __get_cluster_mse__(residuals_all, data_in_cluster):
    residuals_sum = 0
    for element in data_in_cluster:
        residuals_sum += residuals_all[element["id"]] ** 2
    return residuals_sum / len(data_in_cluster)


def __apply_regression__(regr, raster_data, raster_fields):
    """Applies the regression formula to an array, to
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
    """
    if not isinstance(raster_data, np.ndarray) or len(raster_data.shape) != 3:
        raise ValueError("raster_data must be a 3 dimensional array")
    coefs = regr.get_coefs()
    out_data = coefs[1] * np.ones((raster_data[0].shape[0], raster_data[0].shape[1]))

    for i, coef in enumerate(coefs[0]):
        field_pos = raster_fields.index(regr.used_vars[i])
        out_data += coef * raster_data[field_pos]

    return out_data
