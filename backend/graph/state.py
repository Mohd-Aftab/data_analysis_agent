from typing import TypedDict, Optional
import pandas as pd

class AgentState(TypedDict):
    """
    Represents the state of the autonomous data analysis agent.
    """
    user_query : str
    intent: Optional[str]
    
    uploaded_file_path : str
    dataframe : Optional[pd.DataFrame]
    
    profile: Optional[dict]
    preprocessing_summary: Optional[list[str]]
    preprocessing_plan: Optional[list[str]]
    
    eda_result : Optional[dict]
    eda_plan : Optional[list[str]]
    
    visualization_plan: Optional[list[str]]
    
    feature_engineering_plan: Optional[list[dict]]
    
    target_column: Optional[str]
    model: Optional[object]
    model_metrics: Optional[dict]
    model_results: Optional[dict]
    best_model: Optional[object]
    prediction_summary: Optional[dict]
    error: Optional[str]
    
    insights: Optional[list[str]]
    chart_path:Optional[list[str]]
    
    
    # message : str 