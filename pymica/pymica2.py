'''Main class. Calculates data fields from points, using
clusters multi-linear regressions corrected with residuals.
'''
import json
from json import load
from os.path import exists
'''
from multiprocessing.sharedctypes import Value

from interpolation.idw import idw
from interpolation.inverse_distance import inverse_distance
from interpolation.inverse_distance_3d import inverse_distance_3d
from numpy import concatenate, newaxis
from osgeo import gdal, ogr, osr

from pymica.apply_regression import (apply_clustered_regression,
                                     apply_regression)
from pymica.clustered_regression import (ClusteredRegression,
                                         MultiRegressionSigma)
'''

class PyMica:
    '''Main project class. Calculates the regressions, corrects
    them with the interpolated residuals and saves files and gives
    errors.
    '''
    def __init__(self, methodology='id3d', conf='/home/recerca/workspace/pymica/pymica/conf/config_interp.json'):
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
        if methodology not in ['id2d', 'mlr+id2d', 'id3d', 'mlr+id3d','mlr']:
            raise ValueError('Methodology must be \"id2d\", \"id3d\", '
                             '\"mlr+id2d\", \"mlr+id3d\" or \"mlr\"')

        self.config = self.__read_config__(conf)
        
        self.__check_config__(methodology)

    def __read_config__(self,config_file):
        
        #if exists(dirname(abspath(__file__)) + "/config.json"):
        #    config_file = dirname(abspath(__file__)) + "/config.json"
        #elif exists(getcwd() + "/config.json"):
        #    config_file = getcwd() + "/config.json"
        #else:
        #    raise Exception("No es pot trobar el fitxer de configuració")

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                f.close()
        except FileNotFoundError:
            raise FileNotFoundError('Wrong configuration file path.')
        except json.decoder.JSONDecodeError as err:
            raise json.decoder.JSONDecodeError(err.msg, err.doc, err.pos)

        return config

    def __check_config__(self, method):

        if 'id_power' not in self.config[method].keys():
            print('id_power not in the configuration dictionary. ' +
                    'id_power set to default value of 2.5.')
        self.power = self.config.get('id_power', 2.5)

        if 'id_smoothing' not in self.config[method].keys():
            print('id_smoothing not in the configuration dictionary. ' +
                    'id_smoothing set to default value of 0.0.')
        self.smoothing = self.config.get('id_smoothing', 0.0)

        if 'interpolation_bouds' not in self.config[method].keys():
            print('interpolations_bounds not in the configuration dictionary. ' +
                  'interpolations_bounds set to default value of [0, 10000, 0, 10000]')
        self.interpolation_bounds = self.config.get('interpolation_bounds', [0, 10000, 0, 10000])

        if 'resolution' not in self.config[method].keys():
            print('resolution (m) not in the configuration dictionary. ' +
                  'resolution set to default value of 1000 m')
        self.resolution = self.config.get('resolution', 1000)

        if 'EPSG' not in self.config[method].keys():
            print('EPSG not in the configuration dictionary. ' +
                  'EPSG set to default value of 25381')
        self.EPGS = self.config.get('EPSG', 25831)


        if method in ['id3d', 'mlr+id3d']:
            if 'id_penalization' not in self.config[method].keys():
                print('id_penalization not in the configuration dictionary. ' +
                        'id_penalization set to default value of 30.')
            self.penalization = self.config.get('id_penalization', 30.0)

        if method in ['mlr+id2d', 'mlr+id3d','mlr','id3d']:
            if 'variables_files' not in self.config[method].keys():
                raise KeyError('variables_files must be included in the ' +
                                'configuration file if ' + method + ' is ' +
                                'selected.')
            self.variables_files = self.config[method].get('variables_files', None)
            
            if len(self.variables_files.keys()) < 1:
                raise ValueError('variables_files dictionary must have at ' +
                                    'least one key including a variable file ' +
                                    'path containing a 2D predictor field.')
                

    '''
    def interpolate(data_file):
        pass


        
    def save_file(self, file_name):
        #Saves the calculate field data into a file
        #Args:
        #    file_name (str): The output file path
        

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
            d_s = gdal.Oconfig = json.load(f)
                f.close()osr.SpatialReference()
        self.out_proj.ImportFromWkt(d_s.GetProjection())
        self.size = (d_s.RasterYSize, d_s.RasterXSize)
        self.geotransform = d_s.GetGeoTransform()
        d_s = None
    '''


if __name__ == '__main__':
    inst=PyMica()
