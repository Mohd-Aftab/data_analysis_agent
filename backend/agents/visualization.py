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

    df = state["dataframe"]

    target_column = state.get("target_column")

    if not isinstance(target_column, str) or target_column not in df.columns:
        target_column = None

    print("DataFrame columns:", df.columns.tolist())
    print("Validated target column:", target_column)

    plan = visualization_planner.invoke(
            f"""
            You are an expert data visualization planner for an
            AI-powered data analysis agent.

            Your task is to select the most relevant visualizations
            based on the user's request, dataset profile, EDA results,
            and available target column.

            USER REQUEST:
            {state["user_query"]}

            DATASET PROFILE:
            {state["profile"]}

            EDA SUMMARY:
            {eda_summary}

            TARGET COLUMN:
            {state.get("target_column")}

            AVAILABLE VISUALIZATION TYPES:

            1. target_distribution
            Shows the distribution of values in the target column.
            Use this to understand class balance or the distribution
            of the outcome variable.

            2. numerical_distribution
            Shows the distribution of a numerical feature.
            Useful for understanding skewness, spread, and potential
            outliers.

            3. categorical_distribution
            Shows the frequency distribution of a categorical feature.
            Useful for identifying dominant categories and imbalances.

            4. correlation_heatmap
            Shows correlations between numerical features.
            Does not require a specific column.

            5. feature_target_relationship
            Shows the relationship between a feature and the target.
            Use a suitable feature-target comparison to identify
            patterns that may help explain the target outcome.

            INTENT AND SELECTION RULES:

            1. Understand the user's immediate request.
            - If the user asks for general dataset analysis or EDA,
                select charts that provide a useful overview.
            - If the user asks about a particular feature, prioritize
                visualizations relevant to that feature.
            - If the user explicitly requests target analysis,
                prioritize target-related visualizations when possible.
            - If the user requests specific charts, prioritize those
                charts when they are valid and relevant.
            - Do not generate every available chart by default.

            2. Target-dependent visualizations:
            - target_distribution requires a valid target column.
            - feature_target_relationship requires a valid target
                column and a valid feature column.
            - Use the exact target column supplied in the context.
            - If the target column is None, empty, or unavailable,
                do not select target_distribution or
                feature_target_relationship.
            - Never assume that a column is the target merely because
                its name contains words such as Target, Churn, or Label.
            - Do not invent or infer a target column that has not
                been identified in the supplied context.

            3. Column selection:
            - Select only columns present in the dataset profile.
            - Use exact column names, preserving capitalization,
                spaces, and special characters.
            - For numerical_distribution, select a numerical feature.
            - For categorical_distribution, select a categorical
                feature.
            - For feature_target_relationship, select a feature
                distinct from the target column.
            - For correlation_heatmap, the column field is not needed.
            - Never select an identifier or index column unless it
                is specifically relevant to the user's request.

            4. Use the EDA summary:
            - Consider existing EDA results when selecting charts.
            - Prefer visualizations that add meaningful information.
            - Avoid charts that merely repeat information already
                adequately covered by the EDA results.
            - If EDA results identify interesting distributions,
                imbalances, or relationships, prioritize relevant charts.

            5. Avoid redundant visualizations:
            - Do not select multiple charts that communicate
                essentially the same information without a good reason.
            - Prefer a small, informative set of visualizations.
            - For a broad EDA request, select a balanced combination
                of numerical distributions, categorical distributions,
                and a correlation heatmap when appropriate.
            - Include target-related charts only when a valid target
                exists and those charts are relevant.

            6. Data availability:
            - If a requested visualization cannot be created because
                the necessary column or information is unavailable,
                skip that visualization.
            - Do not invent columns, statistics, or EDA findings.
            - If no visualization provides meaningful insight,
                return an empty charts list.

            OUTPUT REQUIREMENTS:
            - Return output strictly according to the
                VisualizationPlan schema.
            - Each chart must use one of the five supported
                visualization types listed above.
            - Populate the column field with an exact valid column
                name whenever that chart requires one.
            - Do not provide a column for correlation_heatmap.
            - Do not include explanations or unsupported chart types.
            """
        )

    print("Visualization plan:", plan)


    chart_paths = []
    
    valid_charts = []

    for chart in plan.charts:

        if chart.chart_type == "correlation_heatmap":
            valid_charts.append(chart)
            continue

        if chart.chart_type in {
            "target_distribution",
            "feature_target_relationship"
        }:
            if target_column is None:
                continue

        if chart.column and chart.column in df.columns:
            valid_charts.append(chart)

    for chart in valid_charts:

        if chart.chart_type == "target_distribution":

            path = plot_target_distribution(
                df,
                target_column,
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
                    df,
                    chart.column,
                    target_column,
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