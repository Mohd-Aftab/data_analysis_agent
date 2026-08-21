from typing import Literal
from pydantic import BaseModel

class EDAPlan(BaseModel):
    actions : list[
        Literal[
            "numerical_summary",
            "categorical_summary",
            "correlation_analysis",
            "outlier_detection",
            "target_analysis",
            "feature_target_relationship"
        ]
    ]