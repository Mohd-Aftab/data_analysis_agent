import pandas as pd


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load a CSV file into a Pandas DataFrame.
    """

    df = pd.read_csv(file_path)
    df = df.drop(
        columns=["customerID"],
        errors="ignore"
    )

    return df