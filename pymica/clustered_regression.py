'''Runs multiple regressions clustering the data in all the ways is asked for
and takes the best option for each zone
'''
import ogr
from pymica.multiregression import MultiRegressionSigma


class ClusteredRegression:
    '''Calculates multiple linear regressions looking which cluster is better
    '''
    def __init__(self, data, clusters_files,
                 data_format=None,
                 regression_params=None):
        if data_format is None:
            self.data_format = {'id_key': 'id',
                                'y_var': 'temp',
                                'x_vars': ('altitude', 'dist')}
        if regression_params is None:
            self.regression_params = {'sigma_limit': 1.5,
                                      'score_threshold': 0.05}

        regr_all = MultiRegressionSigma(data)
        residuals_all = regr_all.get_residuals()

        self.mse = __get_residuals_mse__(residuals_all)

        self.final_regr = [regr_all]
        self.final_data = [data]
        self.final_cluster_file = None

        for cluster_file in clusters_files:
            cluster_file_regressions = []
            file_mse = 0
            clustered_data = __filter_data_by_cluster__(data,
                                                        cluster_file)
            for data_in_cluster in clustered_data:
                mse_all = __get_cluster_mse__(residuals_all,
                                              data_in_cluster)

                cluster_regression = MultiRegressionSigma(data_in_cluster)
                mse_cluster = __get_residuals_mse__(cluster_regression
                                                    .get_residuals())
                if mse_all > mse_cluster:
                    cluster_file_regressions.append(cluster_regression)
                    file_mse += (mse_cluster * len(data_in_cluster))
                else:
                    cluster_file_regressions.append(regr_all)
                    file_mse += mse_all * len(data_in_cluster)

            file_mse = file_mse / len(data)
            if file_mse < self.mse:
                self.final_regr = cluster_file_regressions
                self.final_data = clustered_data
                self.final_cluster_file = cluster_file
                self.mse = file_mse

    def predict_points(self, x_data):
        '''Returns the predicted values for multiple points given the
           x variables (predictors). The formula applied will depend on
           the cluster where the point is located, so the method classifies
           the points into the different clusters too.

        Args:
            x_data list: the x variable values list
                                             with the var names as the keys

        Returns:
            list: The predicted values
        '''

        clustered_data = __filter_data_by_cluster__(x_data,
                                                    self.final_cluster_file)
        out = [None] * len(x_data)
        x_data_idx = {}
        for i, data in enumerate(x_data):
            x_data_idx[data['id']] = i  # TODO: id must be configurable

        for i, cluster_data in enumerate(clustered_data):
            if cluster_data:
                result = self.final_regr[i].predict_points(cluster_data)
                for data in zip(cluster_data, result):
                    out[x_data_idx[data[0]['id']]] = data[1]
        return out


def __filter_data_by_cluster__(data, cluster):
    ds_in = ogr.Open(cluster)
    layer = ds_in.GetLayer()
    num_clusters = layer.GetFeatureCount()
    classified_data = []
    for _ in range(num_clusters):
        cluster_points = []
        feat = layer.GetNextFeature()
        cluster_geom = feat.GetGeometryRef()
        for point in data:
            point_geom = ogr.Geometry(ogr.wkbPoint)
            point_geom.AddPoint(point['lon'], point['lat'])  # TODO: lon and lat must be configurable keys
            if point_geom.Within(cluster_geom):
                cluster_points.append(point)
        classified_data.append(cluster_points)

    return classified_data


def __get_residuals_mse__(residuals):
    mse = 0
    for i in residuals:
        mse += residuals[i]**2

    return mse/len(residuals)


def __get_cluster_mse__(residuals_all, data_in_cluster):
    residuals_sum = 0
    for element in data_in_cluster:
        residuals_sum += residuals_all[element['id']]**2
    return residuals_sum/len(data_in_cluster)
