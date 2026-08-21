from langchain_openai import ChatOpenAI

from schemas.feature_engineering import FeatureEngineeringPlan

from tools.feature_engineering_tool import (
    log_transform,
    bin_numeric,
    combine_rare_categories,
    create_ratio,
    create_interaction,
)
from tools.profiling_tool import profile_dataframe


llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)

feature_engineering_planner = llm.with_structured_output(
    FeatureEngineeringPlan
)


def feature_engineering_node(state):

    df = state["dataframe"]

    plan = feature_engineering_planner.invoke(
        f"""
        You are a feature engineering planner.

        User request:
        {state["user_query"]}

        Dataset profile:
        {state["profile"]}

        Target column:
        {state.get("target_column")}

        Available operations:

        - log_transform: numerical, non-negative columns
        - bin_numeric: numerical columns
        - combine_rare_categories: categorical columns
        - create_ratio: two related numerical columns
        - create_interaction: two related numerical columns

        Select only transformations that are genuinely useful
        for this dataset and prediction task.

        Do not create unnecessary features.
        Do not use the target column as an input feature.
        Only select columns that actually exist.
        """
    )

    print("Feature engineering plan:", plan)

    for action in plan.actions:

        if action.action == "log_transform":
            df = log_transform(df, action.column)

        elif action.action == "bin_numeric":
            df = bin_numeric(df, action.column)

        elif action.action == "combine_rare_categories":
            df = combine_rare_categories(df, action.column)

        elif action.action == "create_ratio":
            df = create_ratio(
                df,
                action.column,
                action.second_column
            )

        elif action.action == "create_interaction":
            df = create_interaction(
                df,
                action.column,
                action.second_column
            )
    updated_profile = profile_dataframe(df)
    return {
        "dataframe": df,
        "profile": updated_profile,
        "feature_engineering_plan": [
            action.model_dump()
            for action in plan.actions
        ]
    }