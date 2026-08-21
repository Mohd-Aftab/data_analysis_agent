from typing import Literal
from pydantic import BaseModel


class Visualization(BaseModel):

    chart_type: Literal[
            "target_distribution",
            "numerical_distribution",
            "categorical_distribution",
            "correlation_heatmap",
            "feature_target_relationship"]
    column: str | None = None
    
class VisualizationPlan(BaseModel):
    charts: list[Visualization]