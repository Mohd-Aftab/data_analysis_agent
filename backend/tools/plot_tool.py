import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_numerical_distribution(df, column, output_path):
    plt.figure(figsize=(8, 5))
    sns.histplot(df[column].dropna(), kde=True)
    plt.title(f"Distribution of {column}")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path


def plot_correlation_heatmap(df, output_path):
    numerical_df = df.select_dtypes(include="number")

    plt.figure(figsize=(10, 7))
    sns.heatmap(numerical_df.corr(), annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path

def plot_target_distribution(
    df: pd.DataFrame,
    target_column: str,
    output_path: str
):
    ax = df[target_column].value_counts().plot(kind="bar")

    ax.set_title(f"{target_column} Distribution")
    ax.set_xlabel(target_column)
    ax.set_ylabel("Count")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path

def plot_categorical_distribution(df, column, output_path):

    plt.figure(figsize=(8, 5))

    df[column].value_counts().plot(kind="bar")

    plt.title(f"{column} Distribution")
    plt.xlabel(column)
    plt.ylabel("Count")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path

def plot_feature_target_relationship(
    df,
    feature_column,
    target_column,
    output_path
):

    plt.figure(figsize=(8, 5))

    if pd.api.types.is_numeric_dtype(df[feature_column]):

        sns.boxplot(
            data=df,
            x=target_column,
            y=feature_column
        )

    else:

        pd.crosstab(
            df[feature_column],
            df[target_column],
            normalize="index"
        ).plot(kind="bar")

    plt.title(
        f"{feature_column} vs {target_column}"
    )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path