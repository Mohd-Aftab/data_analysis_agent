from graph.state import AgentState

def uppercase_node(state : AgentState):
    print("Upper Case node execution")
    
    return {
        "message" : state["message"].upper()
    }