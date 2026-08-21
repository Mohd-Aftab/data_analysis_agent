import re
from graph.state import AgentState
from schemas.planner_schema import PlannerOutput
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)

planner = llm.with_structured_output(PlannerOutput)

def planner_node(state: AgentState):

    query = state["user_query"].lower()
    profile = state["profile"]

    result = planner.invoke(
        f"""
        You are a data analysis planner.

        User request:
        {query}

        Dataset profile:
        {profile}

        Determine the primary action the user is asking the system
        to perform RIGHT NOW.

        Possible intents:
        - preprocessing
        - eda
        - prediction
        - visualization
        - unknown

        Intent definitions:

        1. preprocessing
        Choose this when the user asks to clean, prepare, fix,
        transform, or preprocess the dataset.

        This includes:
        - handling missing values
        - removing duplicates
        - fixing data types
        - removing unnecessary columns
        - preparing data for machine learning

        If the user mentions a future goal such as prediction,
        but is currently asking to prepare the data, choose
        preprocessing.

        2. eda
        Choose this when the user asks to statistically analyze,
        explore, summarize, or understand the dataset.

        This includes:
        - distributions
        - descriptive statistics
        - correlations
        - outliers
        - relationships between variables
        - identifying patterns

        Choose eda when the user wants analysis but does NOT
        specifically request visual output.

        3. visualization
        Choose this when the user explicitly asks to visualize
        the data or create visual output.

        This includes requests containing concepts such as:
        - create charts
        - create graphs
        - plot the data
        - visualize
        - show visually
        - generate visualizations
        - create plots
        - visualize relationships or distributions

        If the user asks for both analysis and visualizations,
        choose visualization because generating visual output
        is explicitly requested.

        4. prediction
        Choose this only when the user is actually asking to:
        - build a predictive model
        - predict a target
        - classify records
        - forecast a value
        - estimate an outcome

        If the intent is prediction, identify the most appropriate
        target column from the available columns.

        5. unknown
        Choose this when the request does not clearly match
        any of the above intents.

        Important rules:

        - Determine what the user wants the system to DO right now,
        not merely the overall business goal mentioned in the query.
        - Do not confuse a future goal with the current action.
        - Do not invent a target column.
        - If the requested target does not exist in the dataset,
        return target_column as None.
        - For preprocessing, eda, and visualization, target_column
        can be None unless a target is clearly relevant.
        """
    )
    
    print("Output:", result)
    
    return {
        "intent": result.intent,
        "target_column": result.target_column
    }