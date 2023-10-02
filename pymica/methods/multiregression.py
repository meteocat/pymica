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

    def __init__(self, data,
                 id_key='id',
                 y_var='temp', x_vars=('altitude', 'dist'),
                 score_threshold=0.05):
        """
        Args:
            data (list): The input data, as a list of dicts
                         with the id, y_var and x_vars values
            id_key (str, optional): Defaults to 'id'.
                                The identifier key name
            y_var (str, optional): Defaults to 'temp'.
                                   The dict key used for the y variable
            x_vars (seq, list, optional): Defaults to ['altitude', 'dist'].
                                     The dict keys used for the x variable
            score_threshold (float): Defaults to 0.05.
                                     The maximum score improvement that
                                     prevents the function adding
                                     more variables
        """

        self.score_threshold = score_threshold
        self.x_vars = list(x_vars)
        self.y_var = y_var
        self.data = data
        self.id_key = id_key

        self._init_multiregression()

    def _init_multiregression(self):

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
            self.y_data.append(value[self.y_var])
            self.keys.append(value[self.id_key])

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

    def _prepare_x_data(self, x_var):
        data = []
        for var in self.used_vars:
            data.append(self.x_data[var])
        if x_var is not None:
            data.append(self.x_data[x_var])
        return list(zip(*data))

    def get_coefs(self):
        '''Returns the regression coefficients and independent term

        Returns:
            list: The n coefficients and then the intercept or independent term
        '''

        return [self.regr.coef_, self.regr.intercept_]

    def get_score(self):
        '''Returns the global regression score

        Returns:
            float: The score from 0 to 1
        '''

        return self.score

    def get_mae(self):
        """Returns the regression's Mean Absolute Error

        Returns:
            float: The MAE value
        """

        predict = self.regr.predict(self.x_final_data)
        return mean_absolute_error(self.y_data, predict)

    def get_mse(self):
        """Returns the regression's Mean Square Error

        Returns:
            float: The MSE value
        """

        predict = self.regr.predict(self.x_final_data)
        return mean_squared_error(self.y_data, predict)

    def get_residuals(self):
        """Returns all the regression residuals
        (predicted value minus the actual value)

        Returns:
            dict: A dict where the key is the id of the data
                  and the value the residual
        """
        predict = self.regr.predict(self.x_final_data)
        residuals_array = predict - self.y_data

        residuals = {}
        i = 0
        for key in self.keys:
            residuals[key] = residuals_array[i]
            i += 1
        return residuals

    def predict_point(self, x_data):
        """Returns the predicted value given the x variables (predictors)

        Args:
            x_data (Dict[str, float]): the x variable values with
                                       the var names as the keys

        Returns:
            float: The predicted value
        """

        data = [[]]
        for var in self.used_vars:
            data[0].append(x_data[var])

        predict = self.regr.predict(data)
        return predict[0]

    def predict_points(self, x_data):
        """Returns the predicted values for multiple points given the
           x variables (predictors)

        Args:
            x_data (List[Dict[str, float]]): the x variable values list
                                             with the var names as the keys

        Returns:
            List[float]: The predicted values
        """

        data = []
        for point_data in x_data:
            point_vars = []
            for var in self.used_vars:
                point_vars.append(point_data[var])
            data.append(point_vars)
        predict = self.regr.predict(data)
        return predict

    def apply_regression(self, raster_data, raster_fields):
        '''Applies the regression formula to an array, to
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
        '''
        if not type(raster_data) == np.ndarray or len(raster_data.shape) != 3:
            raise ValueError("raster_data must be a 3 dimensional array")
        coefs = self.get_coefs()
        out_data = coefs[1] * ones((raster_data[0].shape[0],
                                    raster_data[0].shape[1]))

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
            if (abs(residues[key]) < sigma * sigma_limit or abs(
                    residues[key]) < limit):

                new_data.append(self.data[i])
            i += 1
        self.original_data = self.data.copy()
        self.data = new_data
        self._init_multiregression()

    def get_residuals(self):
        """Returns all the regression residuals
        (predicted value minus the actual value)
        including the points eliminated because of
        the sigma value

        Returns:
            dict: A dict where the key is the id of the data
                  and the value the residual
        """
        y_data = []
        keys = []
        for point in self.original_data:
            point_values = []
            for var in self.x_data:
                point_values.append(point[var])
            y_data.append(point[self.y_var])
            keys.append(point[self.id_key])

        predict = self.predict_points(self.original_data)

        residuals_array = predict - y_data
        residuals = {}

        i = 0
        for key in keys:
            residuals[key] = residuals_array[i]
            i += 1
        return residuals
    
    def get_coefs(self):
        '''Returns the regression coefficients and independent term

        Returns:
            list: The n coefficients and then the intercept or independent term
        '''

        return [self.regr.coef_, self.regr.intercept_]
    
    def apply_regression(self, raster_data, raster_fields):
        '''Applies the regression formula to an array, to
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
        '''
        if not type(raster_data) == np.ndarray or len(raster_data.shape) != 3:
            raise ValueError("raster_data must be a 3 dimensional array")
        coefs = self.get_coefs()
        out_data = coefs[1] * ones((raster_data[0].shape[0],
                                    raster_data[0].shape[1]))

        for i, coef in enumerate(coefs[0]):
            field_pos = raster_fields.index(self.used_vars[i])
            out_data += coef * raster_data[field_pos]

        return out_data
