'''Main class. Calculates data fields from points, using
clusters multi-linear regressions corrected with residuals.
'''
import json

import gdal
import ogr
import osr
from interpolation.inverse_distance import inverse_distance
from numpy import concatenate, newaxis
from pymica.apply_regression import (apply_clustered_regression,
                                     apply_regression)
from pymica.clustered_regression import (ClusteredRegression,
                                         MultiRegressionSigma)


class PyMica:
    '''Main project class. Calculates the regressions, corrects
    them with the interpolated residuals and saves files and gives
    errors.
    '''
    def __init__(self, data_file, variables_file,
                 clusters=None, data_format=None):
        if data_format is None:
            self.data_format = {'loc_vars': ('lon', 'lat'),
                                'id_key': 'id',
                                'y_var': 'temp',
                                'x_vars': ('altitude', 'dist')}
        else:
            self.data_format = data_format

        with open(data_file, "r") as f_p:
            data = json.load(f_p)

        self.__read_variables_files__(variables_file)

        in_proj = osr.SpatialReference()
        in_proj.ImportFromEPSG(4326)

        transf = osr.CoordinateTransformation(in_proj, self.out_proj)

        if clusters:
            d_s = gdal.Open(clusters['mask_file'])
            mask = d_s.ReadAsArray()
            d_s = None

            cl_reg = ClusteredRegression(data, clusters['clusters_files'],
                                         data_format=self.data_format)

            out_data = apply_clustered_regression(cl_reg, self.variables,
                                                  self.data_format['x_vars'],
                                                  mask)
        else:
            cl_reg = MultiRegressionSigma(data)
            out_data = apply_regression(cl_reg, self.variables,
                                        self.data_format['x_vars'])

        residuals = cl_reg.get_residuals()
        residuals_data = {}

        for point in data:
            geom = ogr.Geometry(ogr.wkbPoint)
            geom.AddPoint(point[self.data_format['loc_vars'][0]],
                          point[self.data_format['loc_vars'][1]])
            geom.Transform(transf)

            residuals_data[point[
                           self.data_format['id_key']]] = {
                               'value': residuals[point[
                                    self.data_format['id_key']]],
                               'x': geom.GetX(), 'y': geom.GetY()}

        residuals_field = inverse_distance(residuals_data, self.size,
                                           self.geotransform)

        self.result = out_data - residuals_field

    def save_file(self, file_name):
        '''Saves the calculate field data into a file

        Args:
            file_name (str): The output file path
        '''

        driver = gdal.GetDriverByName('GTiff')
        d_s = driver.Create(file_name, self.size[0], self.size[1], 1,
                            gdal.GDT_Float32)
        d_s.SetGeoTransform(self.geotransform)
        d_s.SetProjection(self.out_proj.ExportToWkt())

        d_s.GetRasterBand(1).WriteArray(self.result)

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
        self.size = (d_s.RasterXSize, d_s.RasterYSize)
        self.geotransform = d_s.GetGeoTransform()
        d_s = None
