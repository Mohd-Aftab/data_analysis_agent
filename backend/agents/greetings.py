from graph.state import AgentState

def greeting_node(state : AgentState):
    print("Greeting node executed")
    
    return {
        "message" : state["message"] + " from greeting node"
    }
