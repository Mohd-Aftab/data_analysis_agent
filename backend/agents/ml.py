from graph.state import AgentState

from langchain_openai import ChatOpenAI

from schemas.ml import MLPlan
from tools.sklearn_tool import train_model 
from schemas.models import MODEL_FACTORY


llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)

ml_planner = llm.with_structured_output(MLPlan)

def ml_node(state: AgentState):

    try:
        
        plan = ml_planner.invoke(
                f"""
                You are an ML planning agent.

                Dataset profile:
                {state["profile"]}

                Target column:
                {state["target_column"]}

                Determine:
                1. Whether this is classification or regression.
                2. Select 2 suitable candidate models for the task.

                Available models:

                Classification:
                - logistic_regression
                - random_forest_classifier

                Regression:
                - linear_regression
                - random_forest_regressor

                Return exactly 2 suitable models.
                Only select models appropriate for the identified task.
                """
            )
        
        df = state["dataframe"]
        target_column = state["target_column"]

        if not target_column:
            return {
                "error": "Could not identify a target column."
            }

        if target_column not in df.columns:
            return {
                "error": f"Target column '{target_column}' not found."
            }
            
        print("ML Plan:", plan)
        
        results= {}
        
        for model_name in plan.models:
            model = MODEL_FACTORY.get(model_name)
            model, metrics = train_model(
                                df,
                                target_column,
                                model
                            )
            results[model_name] = {
                "model": model,
                "metrics": metrics
            }
        
        if plan.task_type == "classification":

            best_model_name = max(
                results,
                key=lambda name: results[name]["metrics"]["f1"]
            )

        else:

            best_model_name = max(
                results,
                key=lambda name: results[name]["metrics"]["r2"]
            )
            
        return {
            "model": results[best_model_name]["model"],
            "model_metrics": results[best_model_name]["metrics"],
            "model_results": results,
            "best_model": best_model_name
        }

    except Exception as e:
        print("Error in ml_node:", str(e))
        return {
            "error": str(e)
        }