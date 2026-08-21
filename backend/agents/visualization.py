from langchain_openai import ChatOpenAI

from schemas.visualization import VisualizationPlan
from tools.plot_tool import (
    plot_numerical_distribution, 
    plot_correlation_heatmap, 
    plot_target_distribution,
    plot_categorical_distribution,
    plot_feature_target_relationship
)


llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)

visualization_planner = llm.with_structured_output(
    VisualizationPlan
)


def visualization_node(state):
    
    eda_summary = {
            "actions": state.get("eda_plan"),
            "result_keys": list((state.get("eda_result") or {}).keys())
        }
    
    print("EDA result:", state.get("eda_result"))

    plan = visualization_planner.invoke(
        f"""
        You are a data visualization planner.

        User request:
        {state["user_query"]}

        Dataset profile:
        {state["profile"]}

        EDA summary:
        {eda_summary}

        Target column:
        {state.get("target_column")}

        Available visualizations:

        - target_distribution
        - numerical_distribution
        - categorical_distribution
        - correlation_heatmap
        - feature_target_relationship

        For visualizations that operate on a specific column,
        select the most relevant column from the dataset.

        For correlation_heatmap, no column is required.

        Select only visualizations that provide meaningful insight.

        IMPORTANT:
        - Only use columns that actually exist in the dataset.
        - Do not invent column names.
        - Do not select unnecessary charts.
        """
    )

    print("Visualization plan:", plan)


    chart_paths = []
    
    valid_charts = []

    df = state["dataframe"]

    for chart in plan.charts:

        if chart.chart_type == "correlation_heatmap":
            valid_charts.append(chart)
            continue

        if chart.column and chart.column in df.columns:
            valid_charts.append(chart)

    for chart in valid_charts:

        if chart.chart_type == "target_distribution":

            path = plot_target_distribution(
                state["dataframe"],
                state["target_column"],
                "outputs/charts/target_distribution.png"
            )

            chart_paths.append(path)

        elif chart.chart_type == "numerical_distribution":

            path = plot_numerical_distribution(
                state["dataframe"],
                chart.column,
                f"outputs/charts/{chart.column}_distribution.png"
            )

            chart_paths.append(path)

        elif chart.chart_type == "correlation_heatmap":

            path = plot_correlation_heatmap(
                state["dataframe"],
                "outputs/charts/correlation_heatmap.png"
            )

            chart_paths.append(path)
        
        elif chart.chart_type == "categorical_distribution":

            path = plot_categorical_distribution(
                state["dataframe"],
                chart.column,
                f"outputs/charts/{chart.column}_distribution.png"
            )

            chart_paths.append(path)


        elif chart.chart_type == "feature_target_relationship":

            path = plot_feature_target_relationship(
                state["dataframe"],
                chart.column,
                state["target_column"],
                f"outputs/charts/{chart.column}_vs_target.png"
            )

            chart_paths.append(path)

    return {
        "visualization_plan": [
            chart.model_dump()
            for chart in valid_charts
        ],
        "chart_paths": chart_paths
    }