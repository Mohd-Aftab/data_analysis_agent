from langchain_openai import ChatOpenAI

from schemas.insights import InsightsOutput


llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)

insights_llm = llm.with_structured_output(InsightsOutput)


def insights_node(state):
    
    eda_summary = {
                "actions": state.get("eda_plan"),
                "result_keys": list((state.get("eda_result") or {}).keys())
            }

    result = insights_llm.invoke(
        f"""
        You are a data analyst.

        User request:
        {state["user_query"]}

        Dataset profile:
        {state["profile"]}

        EDA plan:
        {state.get("eda_plan")}

        EDA results:
        {eda_summary}

        Model results:
        {state.get("model_results")}

        Best model:
        {state.get("best_model")}

        Best model metrics:
        {state.get("model_metrics")}

        Visualization plan:
        {state.get("visualization_plan")}

        Provide:
        1. A concise summary.
        2. Key findings.
        3. Practical recommendations.

        Rules:
        - Only use information provided above.
        - Do not invent statistics.
        - Do not claim causation.
        - Clearly distinguish observations from predictions.
        """
    )

    return {
        "insights": result.model_dump()
    }