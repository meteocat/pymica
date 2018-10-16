"""
Calculates a multiple linear regression recursively adding variables,
until the score is under a threshold
"""
from typing import Dict, List, Union

from numpy import array, std
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


class MultiRegression:
    """
    Calculates a multiple linear regression given the provided data.
    There is a maximum score that prevents adding more variables if reached.
    """

    def __init__(self, data: List[Dict[str, Union[str, float]]],
                 id: str = 'id',
                 y_var: str = 'temp', x_vars: list = ['altitude', 'dist'],
                 score_threshold: float = 0.05):
        """
        Args:
            data (list): The input data, as a list of dicts
                         with the id, y_var and x_vars values
            id (str, optional): Defaults to 'id'.
                                The identifier key name
            y_var (str, optional): Defaults to 'temp'.
                                   The dict key used for the y variable
            x_vars (list, optional): Defaults to ['altitude', 'dist'].
                                     The dict keys used for the x variable
            score_threshold (float): Defaults to 0.05.
                                     The maximum score improvement that
                                     prevents the function adding
                                     more variables
        """

        self.regr = LinearRegression()
        self.score_threshold = score_threshold
        self.x_vars = x_vars
        self.y_var = y_var
        self.data = data
        self.id = id

        self._init_multiregression()

    def _init_multiregression(self):

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
            self.keys.append(value[self.id])

        left_vars = self.x_vars[:]
        final_score = 0

        while len(left_vars) > 0:
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
        return [self.regr.coef_, self.regr.intercept_]

    def get_vars_coefs(self):
        vars_coefs = {"residual": self.regr.intercept_}
        for i in range(len(self.used_vars)):
            vars_coefs[self.used_vars[i]] = self.regr.coef_[i]

        return vars_coefs

    def get_score(self):
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

    def predict_point(self, x_data: Dict[str, float]):
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

    def predict_points(self, x_data: List[Dict[str, float]]):
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


class MultiRegressionSigma(MultiRegression):
    def __init__(self,  *args, sigma_limit=1.5, **kwargs):
        """
        Calculates a multiple linear regression like in :meth:`MultiRegression`
        and eliminates the points where the data error is bigger than a
        threshold before re-calculating the regression again.
        The idea is geting a better fitting function.

        The class inherits all the parameters and methods from
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
        residues = self.get_residuals()
        sigma = std(array(list(residues.values())))
        # self._init_multiregression()
        new_data = []
        i = 0
        for key in residues.keys():
            if (abs(residues[key]) < sigma * sigma_limit or abs(
                    residues[key]) < limit):

                new_data.append(self.data[i])
            i += 1
        self.data = new_data
        self._init_multiregression()
