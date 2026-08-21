from typing import Literal
from pydantic import BaseModel

class PlannerOutput(BaseModel):
    intent: Literal["prediction", "eda", "preprocessing", "visualization", "unknown"]
    target_column: str | None
    