from agents.feature_engineering import feature_engineering_node
from langgraph.graph import StateGraph, START, END

from graph.state import AgentState

from graph.edges import route_after_ml, route_from_planner, route_from_profiling

from agents.planner import planner_node
from agents.preprocessing import preprocessing_node
from agents.eda import eda_node
from agents.error import error_node
from agents.profiling import profiling_node
from agents.ml import ml_node
from agents.insights import insights_node
from agents.visualization import visualization_node


builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("profiling", profiling_node)
builder.add_node("preprocessing", preprocessing_node)
builder.add_node("eda", eda_node)
builder.add_node("error", error_node)
builder.add_node("ml", ml_node)
builder.add_node("insights", insights_node)
builder.add_node("visualization", visualization_node)
builder.add_node("feature_engineering", feature_engineering_node)

builder.add_edge(START, "profiling")
builder.add_edge("profiling", "planner")

builder.add_conditional_edges(
    "planner",
    route_from_planner
)

builder.add_edge("preprocessing", "feature_engineering")
builder.add_edge("feature_engineering", "ml")
builder.add_conditional_edges(
    "ml", 
    route_after_ml
)
builder.add_edge("eda", "visualization")
builder.add_edge("visualization", "insights")
builder.add_edge("insights", END)
builder.add_edge("error", END)

graph = builder.compile()