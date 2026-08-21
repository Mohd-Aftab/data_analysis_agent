from langchain_openai import ChatOpenAI

from graph.state import AgentState
from tools.csv_tool import load_csv

from tools.preprocessing_tool import convert_numeric_columns, handle_missing_values, remove_duplicates
from tools.profiling_tool import profile_dataframe

from schemas.preprocessing import PreprocessingPlan

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)

preprocessing_planner = llm.with_structured_output(PreprocessingPlan)

def preprocessing_node(state: AgentState):
    
    df = state["dataframe"]
    profile = state["profile"]
    observation = []
    
    # drop the customerID column if present; pass the column name (string), not the Series
    df = df.drop(columns=["customerID"], errors="ignore")
    
    plan = preprocessing_planner.invoke(
        f"""
        You are a data preprocessing planner.

        User request:
        {state["user_query"]}

        Dataset profile:
        {state["profile"]}

        Available preprocessing actions:

        - convert_numeric
        - remove_duplicates
        - handle_missing_values
        - remove_constant_columns

        Select only the actions that are actually required.

        Do not select an action simply because it is available.
        Do not invent problems that are not present in the dataset.
        """
    )
    
    print("Preprocessing Plan:", plan)
    
    for action in plan.actions:
        if action == "convert_numeric":
            df = convert_numeric_columns(df)
            observation.append("Numeric columns converted.")
        elif action == "remove_duplicates":
            df = remove_duplicates(df)
            observation.append("Duplicate rows removed.")
            
        elif action == "handle_missing_values":
            df = handle_missing_values(df)
            observation.append("Missing values handled.")
            
    
        
    if not observation:
        observation.append("No preprocessing needed.")     
    
    updated_profile = profile_dataframe(df)
    
    # print(df.head())
    
    return {
        "dataframe" : df,
        "profile" : updated_profile,
        "preprocessing_summary" : observation,
        "preprocessing_plan": plan.actions,
    }