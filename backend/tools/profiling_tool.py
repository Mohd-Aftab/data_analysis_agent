import pandas as pd

from schemas.dataset_profile import DatasetProfile


def profile_dataframe(df: pd.DataFrame):

    profile = {

        "rows": len(df),

        "columns": len(df.columns),

        "column_names": list(df.columns),

        "dtypes": df.dtypes.astype(str).to_dict(),

        "missing_values": df.isnull().sum().to_dict(),

        "duplicates": int(df.duplicated().sum()),

        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2
        )

    }

    return profile