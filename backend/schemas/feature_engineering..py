from typing import Literal
from pydantic import BaseModel


class FeatureEngineeringAction(BaseModel):
    action: Literal[
        "log_transform",
        "bin_numeric",
        "combine_rare_categories",
        "create_ratio",
        "create_interaction"
    ]
    column: str | None = None
    second_column: str | None = None


class FeatureEngineeringPlan(BaseModel):
    actions: list[FeatureEngineeringAction]