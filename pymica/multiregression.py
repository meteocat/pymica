"""
Calculates a multiple linear regression recursively adding variables,
until the score is under a threshold
"""
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


class MultiRegression:

    def __init__(self, data, y_var='temp', x_vars=['altitude', 'dist']):
        self.regr = LinearRegression()
        self.x_data = {}
        self.used_vars = []

        for x_var in x_vars:
            self.x_data[x_var] = []
        self.y_data = []
        self.keys = sorted(data.keys())
        for key in self.keys:
            for x_var in x_vars:
                self.x_data[x_var].append(data[key][x_var])
            self.y_data.append(data[key][y_var])

        left_vars = x_vars[:]
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

                if max_score - final_score > 0.05:
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
        predict = self.regr.predict(self.x_final_data)
        return mean_absolute_error(self.y_data, predict)

    def get_mse(self):
        predict = self.regr.predict(self.x_final_data)
        return mean_squared_error(self.y_data, predict)

    def get_residuals(self):
        predict = self.regr.predict(self.x_final_data)
        residuals_array = predict - self.y_data

        residuals = {}
        i = 0
        for key in self.keys:
            residuals[key] = residuals_array[i]
            i += 1
        return residuals

    def predict_point(self, x_data):
        data = [[]]
        for var in self.used_vars:
            data[0].append(x_data[var])

        predict = self.regr.predict(data)
        return predict[0]

    def predict_points(self, x_data):
        data = []
        for point_data in x_data:
            point_vars = []
            for var in self.used_vars:
                point_vars.append(point_data[var])
            data.append(point_vars)
        predict = self.regr.predict(data)
        return predict
