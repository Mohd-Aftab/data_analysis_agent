from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor
)


MODEL_FACTORY = {
    "logistic_regression": LogisticRegression(max_iter=1000),
    "random_forest_classifier": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    ),
    "linear_regression": LinearRegression(),
    "random_forest_regressor": RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )
}