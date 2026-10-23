from graph.state import AgentState

PLANNER_ROUTES = {
    "prediction": "profiling",
    "eda": "profiling",
}

PROFILE_ROUTES = {
    "prediction": "preprocessing",
    "eda": "eda",
    "preprocessing": "preprocessing",
    "visualization": "visualization",
    "unknown": "error"
}


def route_from_planner(state: AgentState):
    return PROFILE_ROUTES.get(state["intent"], "error")


def route_from_profiling(state: AgentState):
    return PROFILE_ROUTES.get(state["intent"], "error")

def route_after_ml(state: AgentState):

    if state.get("error"):
        print(state.get("error"))
        return "error"

    return "visualization"

def route_after_feature_engineering(state: AgentState):
    if state.get("intent") == "prediction":
        return "ml"
    return "insights"