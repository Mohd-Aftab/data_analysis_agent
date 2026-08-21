from langchain_openai import ChatOpenAI

from schemas.eda import EDAPlan

from tools.eda_tool import (
    feature_target_relationship,
    numerical_summary,
    categorical_summary,
    correlation_matrix,
    outlier_detection,
    target_analysis,
)


llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)

eda_planner = llm.with_structured_output(EDAPlan)


def eda_node(state):

    profile = state["profile"]
    target_column = state.get("target_column")

    plan = eda_planner.invoke(
        f"""
        You are an exploratory data analysis planner.

        Dataset profile:
        {profile}

        Target column:
        {target_column}

        Available EDA actions:

        - numerical_summary
        - categorical_summary
        - correlation_analysis
        - outlier_detection
        - target_analysis
        - feature_target_relationship

        Select the EDA actions that are relevant
        for understanding this dataset and the user's request.

        Do not select unnecessary actions.
        Only select actions that can be supported
        by the available dataset information.
        """
    )

    results = {}

    for action in plan.actions:

        if action == "numerical_summary":
            results[action] = numerical_summary(
                state["dataframe"]
            )

        elif action == "categorical_summary":
            results[action] = categorical_summary(
                state["dataframe"]
            )

        elif action == "correlation_analysis":
            results[action] = correlation_matrix(
                state["dataframe"]
            )

        elif action == "outlier_detection":
            results[action] = outlier_detection(
                state["dataframe"]
            )

        elif action == "target_analysis":
            results[action] = target_analysis(
                state["dataframe"],
                target_column
            )
        elif action == "feature_target_relationship":

            results[action] = feature_target_relationship(
                state["dataframe"],
                target_column
            )

    return {
        "eda_plan": plan.actions,
        "eda_result": results
    }