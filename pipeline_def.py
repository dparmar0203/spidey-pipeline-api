import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class DistrictFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self, first_last_scale=50.0):
        self.first_last_scale = first_last_scale

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.column_stack([
            X["late_night_ratio"].to_numpy(),
            X["first_last_density"].to_numpy() / self.first_last_scale,
            X["verified_ratio"].to_numpy(),
            1 - X["patrol_activity_score"].to_numpy(),
            1 - X["nightlife_score"].to_numpy(),
            X["residential_score"].to_numpy(),
        ])

    def get_feature_names_out(self, input_features=None):
        return np.array([
            "late_night_ratio",
            "first_last_density",
            "verified_ratio",
            "quietness",
            "low_profile",
            "residential_score",
        ])
