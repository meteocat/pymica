"""Main class. Calculates data fields from points, using clusters multi-linear
regressions corrected with residuals.
"""
import json

import numpy as np
from genericpath import exists
from osgeo import gdal, osr, ogr
from pymica.methods.inverse_distance import inverse_distance
from pymica.methods.inverse_distance_3d import inverse_distance_3d

from pymica.methods.clustered_regression import (
    ClusteredRegression,
    MultiRegressionSigma,
)


class PyMica:
    """Main project class. Calculates regressions, corrects them with interpolated
    residuals, saves the results into raster files and calculates errors.
    """

    def __init__(self, methodology: str, config: dict) -> None:
        """Implements different checks to config depending on the chosen methodology.

        Args:
            methodology (str): Interpolation method among 'id2d', 'id3d', 'mlr',
                'mlr+id2d' and 'mlr+id3d'.
            config (dict): Configuration dictionary.

        Raises:
            ValueError: If `methodology` not in 'id2d', 'id3d', 'mlr', 'mlr+id2d'
                and 'mlr+id3d'.
        """
        if methodology not in ["id2d", "mlr+id2d", "id3d", "mlr+id3d", "mlr"]:
            raise ValueError(
                'Methodology must be "id2d", "id3d", "mlr+id2d", "mlr+id3d" or "mlr"'
            )

        self.methodology = methodology
        self.config = self.__read_config__(config)

        self.__check_config__(methodology)

        self.__get_geographical_parameters__()

        if methodology in ["mlr", "id3d", "mlr+id2d", "mlr+id3d"]:
            self.__check_variables__()
            self.__read_variables_files__()

    def __read_config__(self, config_file: str) -> dict:
        """Read configuration file and return it as a dictionary.

        Args:
            config_file (str): Path to a configuration file.

        Raises:
            FileNotFoundError: If `config_file` not found.
            json.decoder.JSONDecodeError: If `config_file` is bad formatted.

        Returns:
            dict: Configuration dictionary.
        """
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                f.close()
        except FileNotFoundError:
            raise FileNotFoundError(config_file + " not found.")
        except json.decoder.JSONDecodeError as err:
            raise json.decoder.JSONDecodeError(err.msg, err.doc, err.pos)

        return config

    def __check_config__(self, methodology: str) -> None:
        """Check configuration keys and parameters based on the methodology selected"""
        if methodology not in self.config.keys():
            raise KeyError(methodology + " not defined in the configuration file.")

        if methodology in ["id2d", "id3d", "mlr+id2d", "mlr+id3d"]:
            if "id_power" not in self.config[methodology].keys():
                print(
                    "id_power not in the configuration dictionary. "
                    + "id_power set to default value of 2.5."
                )
            self.power = self.config[methodology].get("id_power", 2.5)

            if "id_smoothing" not in self.config[methodology].keys():
                print(
                    "id_smoothing not in the configuration dictionary. "
                    + "id_smoothing set to default value of 0.0."
                )
            self.smoothing = self.config[methodology].get("id_smoothing", 0.0)

        if methodology in ["id3d", "mlr+id3d"]:
            if "id_penalization" not in self.config[methodology].keys():
                print(
                    "id_penalization not in the configuration dictionary. "
                    + "id_penalization set to default value of 30."
                )
            self.penalization = self.config[methodology].get("id_penalization", 30.0)

        self.interpolation_bounds = self.config[methodology].get(
            "interpolation_bounds", None
        )
        if self.interpolation_bounds is None:
            raise KeyError(
                "interpolation_bounds must be defined in the configuration dictionary."
            )
        if type(self.interpolation_bounds) is not list:
            raise TypeError(
                "interpolation_bounds must be a list as [x_min, y_min, x_max, y_max]"
            )
        if len(self.interpolation_bounds) != 4:
            raise ValueError(
                "interpolation_bounds must be a list as [x_min, y_min, x_max, y_max]"
            )

        self.resolution = self.config[methodology].get("resolution", None)
        if self.resolution is None:
            raise KeyError(
                "resolution must be defined in the configuration dictionary."
            )
        if type(self.resolution) is str:
            raise TypeError("resolution must have a valid value in meters.")

        self.EPSG = self.config[methodology].get("EPSG", None)
        if self.EPSG is None:
            raise KeyError("EPSG must be defined in the configuration dictionary.")
        if type(self.EPSG) is not int:
            raise TypeError("EPSG must have a valid int value.")

        if methodology in ["mlr+id2d", "mlr+id3d", "mlr", "id3d"]:
            if "variables_files" not in self.config[methodology].keys():
                raise KeyError(
                    "variables_files must be included in the configuration file if "
                    + methodology
                    + " is selected."
                )
            self.variables_files = self.config[methodology].get("variables_files", None)

            if len(self.variables_files.keys()) < 1:
                raise ValueError(
                    "variables_files dictionary must have at least one key including "
                    "a variable file path containing a 2D predictor field."
                )

    def __check_variables__(self) -> None:
        """Check if the properties of variable fields are the same to each other.

        Raises:
            ValueError: If properties of variable fields are not the same with
                        each other.
        """
        geo_param = np.array(
            [
                self.field_geotransform,
                self.field_proj.ExportToWkt(),
                self.field_size[0],
                self.field_size[1],
            ],
            dtype="object",
        )

        for var in list(self.config[self.methodology]["variables_files"].keys()):
            if not exists(self.config[self.methodology]["variables_files"][var]):
                raise FileNotFoundError(
                    "No such file or directory: "
                    + self.config[self.methodology]["variables_files"][var]
                )
            var_ds = gdal.Open(self.config[self.methodology]["variables_files"][var])

            check_equal = np.array_equal(
                np.array(
                    [
                        var_ds.GetGeoTransform(),
                        var_ds.GetProjectionRef(),
                        var_ds.RasterXSize,
                        var_ds.RasterYSize,
                    ],
                    dtype="object",
                ),
                geo_param,
            )

            if check_equal is False:
                raise ValueError(
                    "Variables properties are not the same. Variables fields must have"
                    " the same GeoTransform, Projection, XSize and YSize."
                )

    def __input_data__(self, input_data: list) -> None:
        """Check and transform input data depending on the selected interpolation
        methodology.

        Args:
            input_data (list): Input data as list of dictionaries with keys including
                at least {'id', 'lat', 'lon', 'value'}.

        Raises:
            KeyError: If id, lat, lon, value keys not included in the input data.
            KeyError: If methodology is 'id3d' or 'mlr+id3d' and 'altitude' variable is
                not included in the data dictionary.
            KeyError: If any variable provided in `variables_files` dictionary missing
                in any of the data dictionaries.

        Returns:
            dict: Formatted input data.
        """
        for elements in input_data:
            if not {"id", "lat", "lon", "value"} < set(elements.keys()):
                raise KeyError(
                    "id, lat, lon, value keys must be included in the imput data"
                )

        if self.methodology in ["id3d", "mlr+id3d"]:
            for elements in input_data:
                if "altitude" not in elements.keys():
                    raise KeyError("altitude must be included in the " "data file")

        if self.methodology in ["mlr", "mlr+id2d", "mlr+id3d"]:
            for elements in input_data:
                if not set(
                    list(self.config[self.methodology]["variables_files"].keys())
                ).issubset(set(list(elements.keys()))):
                    raise KeyError(
                        "Some of the variables provided in the "
                        "variables_files dictionary missing in " + elements["id"] + "."
                    )

        in_proj = osr.SpatialReference()
        in_proj.ImportFromEPSG(4326)
        transf = osr.CoordinateTransformation(in_proj, self.field_proj)

        for point in input_data:
            geom = ogr.Geometry(ogr.wkbPoint)
            geom.AddPoint(point["lat"], point["lon"])
            geom.Transform(transf)

            point["x"] = geom.GetX()
            point["y"] = geom.GetY()

        return input_data

    def __read_variables_files__(self):
        for i, var in enumerate(
            list(self.config[self.methodology]["variables_files"].keys())
        ):
            var_ds = gdal.Open(self.config[self.methodology]["variables_files"][var])
            if i == 0:
                self.variables = np.array([var_ds.ReadAsArray()])
            else:
                self.variables = np.concatenate(
                    (self.variables, np.array([var_ds.ReadAsArray()])), axis=0
                )

        var_ds = None

    def __get_geographical_parameters__(self):
        int_bounds = self.config[self.methodology]["interpolation_bounds"]
        res = self.config[self.methodology]["resolution"]

        self.field_geotransform = (
            float(int_bounds[0]),
            float(res),
            float(0),
            float(int_bounds[3]),
            float(0),
            float(-res),
        )

        self.field_proj = osr.SpatialReference()
        self.field_proj.ImportFromEPSG(self.config[self.methodology]["EPSG"])
        self.field_size = [
            int((int_bounds[3] - int_bounds[1]) / res),
            int((int_bounds[2] - int_bounds[0]) / res),
        ]

    def __get_regression_results__(self, clusters, data):
        if clusters:
            cl_reg = ClusteredRegression(
                data,
                clusters["clusters_files"],
                x_vars=list(self.variables_files.keys()),
            )
            cluster_file_index = clusters["clusters_files"].index(
                cl_reg.final_cluster_file
            )

            d_s = gdal.Open(clusters["mask_files"][cluster_file_index])
            mask = d_s.ReadAsArray()
            d_s = None

            out_data = cl_reg.apply_clustered_regression(
                self.variables, self.data_format["x_vars"], mask
            )
        else:
            cl_reg = MultiRegressionSigma(
                data, x_vars=list(self.variables_files.keys())
            )
            out_data = cl_reg.apply_regression(
                self.variables, list(self.variables_files.keys())
            )

        return cl_reg, out_data

    def interpolate(self, input_data: list) -> np.array:
        """Apply the interpolation methodology to input data.

        Args:
            input_dict (list): Input data as list of dictionaries with keys including
                at least {'id', 'lat', 'lon', 'value'}.

        Returns:
            np.array: Interpolated field.
        """
        data = self.__input_data__(input_data)

        if self.methodology == "id2d":
            field = inverse_distance(
                data,
                self.field_size,
                list(self.field_geotransform),
                self.power,
                self.smoothing,
            )
        elif self.methodology == "id3d":
            field = inverse_distance_3d(
                data,
                list(self.field_size),
                list(self.field_geotransform),
                self.variables[list(self.variables_files.keys()).index("altitude")],
                self.power,
                self.smoothing,
                self.penalization,
            )
        elif self.methodology in ["mlr", "mlr+id2d", "mlr+id3d"]:
            regression, field = self.__get_regression_results__(False, data)

        if self.methodology in ["mlr+id2d", "mlr+id3d"]:
            residues = regression.get_residuals()

            res_interp = []
            for stat in data:
                if stat["id"] in residues.keys():
                    res = {
                        "id": stat["id"],
                        "x": stat["x"],
                        "y": stat["y"],
                        "value": residues[stat["id"]],
                    }
                    if self.methodology == "mlr+id3d":
                        res["altitude"] = stat["altitude"]
                    res_interp.append(res)

            if self.methodology == "mlr+id2d":
                res_field = inverse_distance(
                    res_interp,
                    list(self.field_size),
                    list(self.field_geotransform),
                    self.power,
                    self.smoothing,
                )
            elif self.methodology == "mlr+id3d":
                res_field = inverse_distance_3d(
                    res_interp,
                    list(self.field_size),
                    list(self.field_geotransform),
                    self.variables[list(self.variables_files.keys()).index("altitude")],
                    self.power,
                    self.smoothing,
                    self.penalization,
                )

            field = field - res_field

        self.field = field

        return field

    def save_file(self, file_name: str) -> None:
        """Save the interpolated field into a raster file.

        Args:
            file_name (str): Output file path.
        """
        driver = gdal.GetDriverByName("GTiff")
        d_s = driver.Create(file_name, self.size[1], self.size[0], 1, gdal.GDT_Float32)
        d_s.SetGeoTransform(self.geotransform)
        d_s.SetProjection(self.out_proj.ExportToWkt())

        d_s.GetRasterBand(1).WriteArray(self.field)

        d_s = None
