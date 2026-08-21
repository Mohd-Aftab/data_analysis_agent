import pandas as pd

def numerical_summary(df: pd.DataFrame) -> dict:
    numerical_columns = df.select_dtypes(
        include="number"
    ).columns

    return df[numerical_columns].describe().to_dict()

def categorical_summary(df: pd.DataFrame) -> dict:
    
    categorical_columns  = df.select_dtypes(
        include=["object", "bool", "category"]
    ).columns
    
    return {
        column : df[column].value_counts().to_dict()
        for column in categorical_columns
    }
    
def correlation_matrix(df: pd.DataFrame) -> dict:
    num_df = df.select_dtypes(
        include="number"
    )
    
    if num_df.empty:
        return {}
    
    corr_mat = num_df.corr().round(3).to_dict()
    
    return corr_mat

def outlier_detection(df):

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns

    result = {}

    for column in numerical_columns:

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        count = (
            (df[column] < lower) |
            (df[column] > upper)
        ).sum()

        result[column] = int(count)

    return result
        
def target_analysis(df, target_column):

    return {
        "distribution":
            df[target_column].value_counts().to_dict(),
        "unique_values":
            int(df[target_column].nunique())
    }
    
def feature_target_relationship(df, target_column):

    results = {}

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns

    # Numerical features
    for column in numerical_columns:

        if column == target_column:
            continue

        results[column] = (
            df.groupby(target_column)[column]
            .mean()
            .to_dict()
        )

    # Categorical features
    for column in categorical_columns:

        if column == target_column:
            continue

        results[column] = (
            df.groupby(column)[target_column]
            .apply(lambda x: (x == "Yes").mean())
            .to_dict()
        )

    return results