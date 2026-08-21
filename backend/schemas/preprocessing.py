from typing import Literal
from pydantic import BaseModel


class PreprocessingPlan(BaseModel):

    actions: list[
        Literal[
            "convert_numeric",
            "remove_duplicates",
            "handle_missing_values",
            "remove_constant_columns"
        ]
    ]