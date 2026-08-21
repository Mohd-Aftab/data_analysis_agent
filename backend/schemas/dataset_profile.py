from typing import TypedDict

class DatasetProfile(TypedDict):
    rows: int
    columns: int
    column_names: list[str]
    dtypes: dict[str, str]
    missing_values: dict[str, int]
    duplicates: int
    memory_usage_mb: float