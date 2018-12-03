'''Main class. Calculates data fields from points, using
clusters multi-linear regressions corrected with residuals.
'''
import json

import gdal
import ogr
import osr
from numpy import concatenate, newaxis

from interpolation.inverse_distance import inverse_distance
from pymica.apply_regression import apply_clustered_regression
from pymica.clustered_regression import ClusteredRegression


class PyMica:
    '''Main project class. Calculates the regressions, corrects
    them with the interpolated residuals and saves files and gives
    errors.
    '''
    def __init__(self, data_file, variables_file,
                 clusters_files=None, mask_file=None):
        with open(data_file, "r") as f_p:
            data = json.load(f_p)

        if isinstance(variables_file, (list,)):
            variables = None
            for layer_file in variables_file:
                d_s = gdal.Open(layer_file)
                layer_data = d_s.ReadAsArray()[newaxis, :, :]
                if variables is None:
                    variables = layer_data
                else:
                    variables = concatenate((variables, layer_data),
                                            axis=0)
        else:
            d_s = gdal.Open(variables_file)
            variables = d_s.ReadAsArray()
        self.out_proj = osr.SpatialReference()
        self.out_proj.ImportFromWkt(d_s.GetProjection())
        self.size = (d_s.RasterXSize, d_s.RasterYSize)
        self.geotransform = d_s.GetGeoTransform()
        d_s = None

        d_s = gdal.Open(mask_file)
        mask = d_s.ReadAsArray()
        d_s = None

        in_proj = osr.SpatialReference()
        in_proj.ImportFromEPSG(4326)

        transf = osr.CoordinateTransformation(in_proj, self.out_proj)

        cl_reg = ClusteredRegression(data, clusters_files)

        out_data = apply_clustered_regression(cl_reg, variables,
                                              ['altitude', 'dist'], mask)
        residuals = cl_reg.get_residuals()

        residuals_data = {}
        for point in data:
            geom = ogr.Geometry(ogr.wkbPoint)
            geom.AddPoint(point['lon'], point['lat'])
            geom.Transform(transf)

            residuals_data[point['id']] = {'value': residuals[point['id']],
                                           'x': geom.GetX(), 'y': geom.GetY()}

        residuals_field = inverse_distance(residuals_data, self.size, self.geotransform)

        self.result = out_data - residuals_field
    
    def save_file(self, file_name):
        driver = gdal.GetDriverByName('GTiff')
        d_s = driver.Create(file_name, self.size[0], self.size[1], 1,
                            gdal.GDT_Float32)
        d_s.SetGeoTransform(self.geotransform)
        d_s.SetProjection(self.out_proj.ExportToWkt())

        d_s.GetRasterBand(1).WriteArray(self.result)
