import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    f1_score
)

import numpy as np


def train_model(df, target_column, model):

    X = df.drop(columns=[target_column])
    y = df[target_column]

    numerical_columns = X.select_dtypes(
        include="number"
    ).columns.tolist()
    

    categorical_columns = X.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()
    

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                numerical_columns,
            ),
            (
                "cat",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]),
                categorical_columns,
            ),
        ]
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    # Stratify only for classification models
    if hasattr(model, "predict_proba"):
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
        )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    # Classification
    if hasattr(model, "predict_proba"):

        metrics = {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(
                y_test,
                predictions,
                zero_division=0,
                pos_label="Yes"  # Adjust this based on your dataset
            ),
            "recall": recall_score(
                y_test,
                predictions,
                zero_division=0,
                pos_label="Yes"  # Adjust this based on your dataset
            ),
             "f1": f1_score(
                    y_test,
                    predictions,
                    zero_division=0,
                    pos_label="Yes"  # Adjust this based on your dataset
                )
        }

    # Regression
    else:

        metrics = {
            "mae": mean_absolute_error(y_test, predictions),
            "rmse": np.sqrt(
                mean_squared_error(y_test, predictions)
            ),
            "r2": r2_score(y_test, predictions),
        }

    return pipeline, metrics