from typing import Literal
from pydantic import BaseModel

class MLPlan(BaseModel):
    task_type: Literal["classification", "regression"]
    models: list[Literal[
        "logistic_regression",
        "random_forest_classifier",
        "linear_regression",
        "random_forest_regressor"
    ]]