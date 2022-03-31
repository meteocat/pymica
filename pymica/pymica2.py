'''Main class. Calculates data fields from points, using
clusters multi-linear regressions corrected with residuals.
'''
import json
from multiprocessing.sharedctypes import Value
from tabnanny import check

from interpolation.idw import idw
from interpolation.inverse_distance import inverse_distance
from interpolation.inverse_distance_3d import inverse_distance_3d
from numpy import asarray, concatenate, newaxis, array_equal
import numpy as np
from osgeo import gdal, ogr, osr

from pymica.apply_regression import (apply_clustered_regression,
                                     apply_regression)
from pymica.clustered_regression import (ClusteredRegression,
                                         MultiRegressionSigma)


class PyMica:
    '''Main project class. Calculates the regressions, corrects
    them with the interpolated residuals and saves files and gives
    errors.
    '''
    def __init__(self, methodology, config):
        '''
        Args:
            data_file (str): The path with the point data
            variables_file (str, list): The file(s) path(s) containing the
                                        fields used in the regression
            clusters (dict, optional): Defaults to None. Two keys,
                                        clusters_files and mask_files,
                                        with the paths for the
                                        cluster definitions and merging data
            data_format (dict, optional): Defaults to None. The name of the
                                          variables in the data files.
                                          Defaults to:
                                          {'loc_vars': ('lon', 'lat'),
                                          'id_key': 'id',
                                          'y_var': 'temp',
                                          'x_vars': ('altitude', 'dist')}
            residuals_int (str): The indicator of the residuals interpolation
                                  methodology. Defaults to 'id2d'.
                                  Methodologies available: id2d, id3d and idw.
            z_field (str): The field used as the z variable when using the id3d
                           value as the residuals_int method.
                           Defaults to 'altitude'
            config (dict): Configuration dictionary.
        '''
        if methodology not in ['id2d', 'mlr+id2d', 'id3d', 'mlr+id3d']:
            raise ValueError('Methodology must be \"id2d\", \"id3d\", '
                             '\"mlr+id2d\" or \"mlr+id3d\"')

        if methodology in ['id2d', 'mlr+id2d', 'id3d', 'mlr+id3d']:
            if 'id_power' not in config.keys():
                print('id_power not in the configuration dictionary. '
                      'id_power set to default value of 2.5.')
            self.power = config.get('id_power', 2.5)

            if 'id_smoothing' not in config.keys():
                print('id_smoothing not in the configuration dictionary. '
                      'id_smoothing set to default value of 0.0.')
            self.smoothing = config.get('id_smoothing', 0.0)

        if methodology == 'id3d' or methodology == 'mlr+id3d':
            if 'id_penalization' not in config.keys():
                print('id_penalization not in the configuration dictionary. '
                      'id_penalization set to default value of 30.')
            self.smoothing = config.get('id_penalization', 30.0)

        '''
        if data_format is None:
            self.data_format = {'loc_vars': ('lon', 'lat'),
                                'id_key': 'id',
                                'y_var': 'temp',
                                'x_vars': ('altitude', 'dist')}
        else:
            self.data_format = data_format
        '''
        if 'power' in config.keys():
            self.power = float(config['power'])
        else:
            self.power = 2.5

        if 'smoothing' in config.keys():
            self.smoothing = float(config['smoothing'])
        else:
            self.smoothing = 0.0

        if 'penalization' in config.keys():
            self.penalization = float(config['penalization'])
        else:
            self.penalization = 30.0
        '''
        with open(data_file, "r") as f_p:
            data = json.load(f_p)
        '''
        # self.__read_variables_files__(variables_file)

        in_proj = osr.SpatialReference()
        in_proj.ImportFromEPSG(4326)
        self.config = config
        self.methodology = methodology

        self.__check_variables__()

        # transf = osr.CoordinateTransformation(in_proj, self.out_proj)

        # cl_reg, out_data = self.__get_regression_results(clusters, data)
        '''
        residuals = cl_reg.get_residuals()
        residuals_data = {}

        for point in data:
            geom = ogr.Geometry(ogr.wkbPoint)
            geom.AddPoint(point[self.data_format['loc_vars'][1]],
                          point[self.data_format['loc_vars'][0]])
            geom.Transform(transf)

            if point[self.data_format['id_key']] in residuals:
                residuals_data[point[
                    self.data_format['id_key']]] = {
                    'value': residuals[point[
                        self.data_format['id_key']]],
                    'x': geom.GetX(), 'y': geom.GetY()}

            if residuals_int == 'id3d':
                residuals_data[point[self.data_format['id_key']]
                               ]['z'] = point[z_field]

        if residuals_int == 'id2d':
            residuals_field = inverse_distance(residuals_data,
                                               self.size,
                                               self.geotransform,
                                               power=self.power,
                                               smoothing=self.smoothing)
        elif residuals_int == 'id3d':
            # dem = gdal.Open(
            #     variables_file[self.data_format['x_vars'].index(z_field)])
            # dem = dem.ReadAsArray()
            dem = self.variables[self.data_format['x_vars'].index(z_field)]
            residuals_field = inverse_distance_3d(
                residuals_data, self.size,
                self.geotransform, dem, power=self.power,
                smoothing=self.smoothing, penalization=self.penalization)
        elif residuals_int == 'idw':
            residuals_field = idw(residuals_data, self.size, self.geotransform)
        else:
            raise ValueError("[Errno 2]residuals_int must be \"id2d\"," +
                             " \"id3d\" or \"idw\"")

        self.result = out_data - residuals_field
        '''

    def __check_variables__(self):
        """Checks if the properties of variables are the same with each other.

        Raises:
            ValueError: If properties of variable fields are not the same with
                        each other.
        """
        if len(self.config['variables_files'].keys()) < 2:
            pass
        for i, var in enumerate(list(self.config['variables_files'].keys())):
            var_ds = gdal.Open(self.config['variables_files'][var])
            if i == 0:
                var_md = np.array([var_ds.GetGeoTransform(),
                                   var_ds.GetProjectionRef(),
                                   var_ds.RasterXSize,
                                   var_ds.RasterYSize], dtype='object')
                check_equal = True
            else:
                check_equal = array_equal(np.array([var_ds.GetGeoTransform(),
                                                    var_ds.GetProjectionRef(),
                                                    var_ds.RasterXSize,
                                                    var_ds.RasterYSize],
                                                   dtype='object'),
                                          var_md)
            if check_equal is False:
                raise ValueError('Variables properties are not the same. '
                                 'Variables fields must have the same '
                                 'GeoTransform, Projection, XSize and YSize.')

    def summary(self):
        print('pymica interpolator')
        print('-------------------')
        if self.methodology in ['mlr+id2d', 'id2d']:
            print('Methodology                 : ' + self.methodology)
            print('Inverse distance - power    : ' + str(self.power))
            print('Inverse distance - smoothing: ' + str(self.smoothing))
        if self.methodology in ['mlr+id3d', 'id3d']:
            print('Methodology                    : ' + self.methodology)
            print('Inverse distance - power       : ' + str(self.power))
            print('Inverse distance - smoothing   : ' + str(self.smoothing))
            print('Inverse distance - penalization: ' + str(self.penalization))

    def save_file(self, file_name):
        '''Saves the calculate field data into a file

        Args:
            file_name (str): The output file path
        '''

        driver = gdal.GetDriverByName('GTiff')
        d_s = driver.Create(file_name, self.size[1], self.size[0], 1,
                            gdal.GDT_Float32)
        d_s.SetGeoTransform(self.geotransform)
        d_s.SetProjection(self.out_proj.ExportToWkt())

        d_s.GetRasterBand(1).WriteArray(self.result)

    def __get_regression_results(self, clusters, data):
        if clusters:
            cl_reg = ClusteredRegression(data, clusters['clusters_files'],
                                         data_format=self.data_format)
            cluster_file_index = clusters['clusters_files'].index(
                    cl_reg.final_cluster_file)

            d_s = gdal.Open(clusters['mask_files'][cluster_file_index])
            mask = d_s.ReadAsArray()
            d_s = None

            out_data = apply_clustered_regression(
                                cl_reg, self.variables,
                                self.data_format['x_vars'],
                                mask)
        else:
            cl_reg = MultiRegressionSigma(data,
                                          id_key=self.data_format['id_key'],
                                          y_var=self.data_format['y_var'],
                                          x_vars=self.data_format['x_vars'])
            out_data = apply_regression(cl_reg, self.variables,
                                        self.data_format['x_vars'])

        return cl_reg, out_data

    def __read_variables_files__(self, variables_file):
        if isinstance(variables_file, (list,)):
            self.variables = None
            for layer_file in variables_file:
                d_s = gdal.Open(layer_file)
                if d_s is None:
                    raise FileNotFoundError("[Errno 2] No such file or " +
                                            "directory: 'BadFile'")
                for i in range(d_s.RasterCount):
                    layer_data = d_s.GetRasterBand(i + 1)\
                        .ReadAsArray()[newaxis, :, :]
                    if self.variables is None:
                        self.variables = layer_data
                    else:
                        self.variables = concatenate((self.variables,
                                                      layer_data), axis=0)
        else:
            d_s = gdal.Open(variables_file)
            self.variables = d_s.ReadAsArray()

        self.out_proj = osr.SpatialReference()
        self.out_proj.ImportFromWkt(d_s.GetProjection())
        self.size = (d_s.RasterYSize, d_s.RasterXSize)
        self.geotransform = d_s.GetGeoTransform()
        d_s = None
