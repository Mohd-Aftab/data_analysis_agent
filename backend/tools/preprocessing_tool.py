import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    MVP strategy:
    - Numeric columns -> median
    - Object columns -> mode
    """

    for column in df.columns:

        if df[column].isnull().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(df[column].median())
        else:
            df[column] = df[column].fillna(df[column].mode()[0])

    return df

def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:

    for column in df.select_dtypes(include=["object"]).columns:

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # If most non-null values can be converted,
        # treat the column as numeric.
        original_non_null = df[column].notna().sum()

        if original_non_null == 0:
            continue

        conversion_ratio = converted.notna().sum() / original_non_null

        if conversion_ratio >= 0.95:
            print("COLUMN CONVERTED TO NUMERIC:", column)
            df[column] = converted

    return df