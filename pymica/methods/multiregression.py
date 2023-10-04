"""Calculates a multiple linear regression recursively adding variables,
until the score is under a threshold

For more information, see :ref:`Multiple Linear Regression`.
"""
import numpy as np
from numpy import array, std, ones
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


class MultiRegression:
    """
    Calculates a multiple linear regression given the provided data.
    There is a maximum score that prevents adding more variables if reached.
    """

    def __init__(self, data: list, x_vars: list, score_threshold: float = 0.05) -> None:
        """Call `_init_multiregression`.

        Args:
            data (list): Input data as a list of dicts with at least
                {'id', 'lon', 'lat', 'value'} as keys.
            x_vars (list): Predictor variables to consider in the regression
                calculation. Must be in the data dictionary.
            score_threshold (float, optional): Maximum score improvement that prevent
                the regression adding more variables. Defaults to 0.05.
        """
        self.score_threshold = score_threshold
        self.x_vars = list(x_vars)
        self.data = data

        self._init_multiregression()

    def _init_multiregression(self):
        """Init module for multiregression class.

        Raises:
            ValueError: If none of the predictor variables fits to the predictand
            variable.
        """
        self.regr = LinearRegression()
        self.used_vars = []
        self.x_data = {}

        for x_var in self.x_vars:
            self.x_data[x_var] = []
        self.y_data = []
        self.keys = []
        for value in self.data:
            for x_var in self.x_vars:
                self.x_data[x_var].append(value[x_var])
            self.y_data.append(value["value"])
            self.keys.append(value["id"])

        left_vars = self.x_vars[:]
        final_score = 0

        while left_vars:
            max_score = 0
            chosen_var = None
            for x_var in left_vars:
                x_data = self._prepare_x_data(x_var)
                self.regr.fit(x_data, self.y_data)

                score = self.regr.score(x_data, self.y_data)
                if score > max_score:
                    max_score = score
                    chosen_var = x_var
            if chosen_var is None:
                break
            else:
                left_vars.remove(chosen_var)

                if max_score - final_score > self.score_threshold:
                    final_score = max_score
                    self.used_vars.append(chosen_var)

        if len(self.used_vars) == 0:
            raise ValueError("No variable fits properly")

        self.x_final_data = self._prepare_x_data(None)
        self.regr.fit(self.x_final_data, self.y_data)
        self.score = self.regr.score(self.x_final_data, self.y_data)

    def _prepare_x_data(self, x_var) -> list:
        """Prepare x data for MLR calculations.

        Args:
            x_var (str): Predictor variable name.

        Returns:
            list: `x_var` predictor data.
        """
        data = []
        for var in self.used_vars:
            data.append(self.x_data[var])
        if x_var is not None:
            data.append(self.x_data[x_var])
        return list(zip(*data))

    def get_coefs(self):
        """Regression coefficients and the independent term.

        Returns:
            list: The n coefficients and then the intercept or independent term.
        """
        return [self.regr.coef_, self.regr.intercept_]

    def get_score(self) -> float:
        """Global regression score.

        Returns:
            float: R^2 score.
        """
        return self.score

    def get_mae(self) -> float:
        """Regression's Mean Absolute Error.

        Returns:
            float: The MAE value.
        """
        predict = self.regr.predict(self.x_final_data)

        return mean_absolute_error(self.y_data, predict)

    def get_mse(self) -> float:
        """Regression's Mean Squared Error.

        Returns:
            float: The MSE value.
        """
        predict = self.regr.predict(self.x_final_data)

        return mean_squared_error(self.y_data, predict)

    def get_residuals(self) -> dict:
        """Regression residuals (predicted value minus the actual value) for each id
        location.

        Returns:
            dict: A dictionary where keys are the id of the data point and values the
            residual value.
        """
        predict = self.regr.predict(self.x_final_data)
        residuals_array = predict - self.y_data

        residuals = {}
        for i, key in enumerate(self.keys):
            residuals[key] = residuals_array[i]

        return residuals

    def predict_point(self, x_data: dict) -> float:
        """Predicted value by the regression given the predictor variables.

        Args:
            x_data (Dict[str, float]): the x variable values with
                                       the var names as the keys

        Returns:
            float: The predicted value.
        """
        data = [[]]
        for var in self.used_vars:
            data[0].append(x_data[var])
        predict = self.regr.predict(data)

        return predict[0]

    def predict_points(self, x_data: list) -> list:
        """Predicted values for multiple points given the predictor variables for each.

        Args:
            x_data (list): List of dictionaries with input data. Dictionary must
                include, at least, {'id', 'lon', 'lat', 'value'} as keys.

        Returns:
            list: The predicted values.
        """
        data = []
        for point_data in x_data:
            point_vars = []
            for var in self.used_vars:
                point_vars.append(point_data[var])
            data.append(point_vars)
        predict = self.regr.predict(data)

        return predict

    def apply_regression(self, raster_data: np.array, raster_fields: list) -> np.array:
        """Apply the regression coefficients to an array of predictor variables data.
        The interpolated result is obtained.

        Args:
            raster_data (np.array): A 3-D array with the predictor variables data.
            raster_fields (list): Predictor variable names in the order they are
                provided in `raster_data` to use the predictor fields in the correct
                order.

        Raises:
            ValueError: `raster_data` is not a 3-D array.

        Returns:
            np.array: Interpolated field.
        """
        if not type(raster_data) == np.ndarray or len(raster_data.shape) != 3:
            raise ValueError("`raster_data` must be a 3 dimensional array")
        coefs = self.get_coefs()
        out_data = coefs[1] * ones((raster_data[0].shape[0], raster_data[0].shape[1]))

        for i, coef in enumerate(coefs[0]):
            field_pos = raster_fields.index(self.used_vars[i])
            out_data += coef * raster_data[field_pos]

        return out_data


class MultiRegressionSigma(MultiRegression):
    """Calculates a multiple linear regression like in :meth:`MultiRegression`
    and eliminates the points where the data error is bigger than a
    threshold before re-calculating the regression again.
    The idea is geting a better fitting function.
    """

    def __init__(self, *args, sigma_limit=1.5, **kwargs):
        """The class inherits all the parameters and methods from
        :meth:`MultiRegression`, but adds:

        Args:
            sigma_limit (float, optional): Defaults to 1.5.
                    The maximum error allowed to the data,
                    in multiples of the sigma value.
                    The error that is above this is erased before
                    re-calculating the regression
        """
        limit = 0.1
        super().__init__(*args, **kwargs)
        residues = super().get_residuals()
        sigma = std(array(list(residues.values())))
        new_data = []
        i = 0
        for key in residues:
            if abs(residues[key]) < sigma * sigma_limit or abs(residues[key]) < limit:
                new_data.append(self.data[i])
            i += 1
        self.original_data = self.data.copy()
        self.data = new_data
        self._init_multiregression()

    def get_residuals(self):
        """Regression residuals (predicted value minus the actual value) for each id
        location including the points eliminated because of the sigma value.

        Returns:
            dict: A dictionary where keys are the id of the data point and values the
            residual value.
        """
        y_data = []
        keys = []
        for point in self.original_data:
            point_values = []
            for var in self.x_data:
                point_values.append(point[var])
            y_data.append(point["value"])
            keys.append(point["id"])

        predict = self.predict_points(self.original_data)

        residuals_array = predict - y_data
        residuals = {}

        i = 0
        for key in keys:
            residuals[key] = residuals_array[i]
            i += 1
        return residuals
