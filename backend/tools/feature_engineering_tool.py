import pandas as pd

import numpy as np


def log_transform(df, column):

    if column in df.columns:
        df[f"{column}_log"] = np.log1p(
            df[column].clip(lower=0)
        )

    return df

def bin_numeric(df, column):

    if column in df.columns:

        df[f"{column}_bin"] = pd.qcut(
            df[column],
            q=4,
            labels=[
                "low",
                "medium",
                "high",
                "very_high"
            ],
            duplicates="drop"
        )

    return df

def combine_rare_categories(
    df,
    column,
    threshold=0.05
):

    if column not in df.columns:
        return df

    frequency = df[column].value_counts(
        normalize=True
    )

    rare_categories = frequency[
        frequency < threshold
    ].index

    df[column] = df[column].replace(
        rare_categories,
        "Other"
    )

    return df

def create_ratio(
    df,
    column,
    second_column
):

    if (
        column in df.columns
        and second_column in df.columns
    ):

        df[f"{column}_per_{second_column}"] = (
            df[column] /
            df[second_column].replace(0, np.nan)
        )

    return df

def create_interaction(
    df,
    column,
    second_column
):

    if (
        column in df.columns
        and second_column in df.columns
    ):

        df[f"{column}_x_{second_column}"] = (
            df[column] * df[second_column]
        )

    return df