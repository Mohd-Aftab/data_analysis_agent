from graph.builder import graph

state = {
    "user_query": "predict customer churn",
    "intent": None,
    "uploaded_file_path": "dataset/churn_data.csv",
    "dataframe": None,
    "profile": None
}

result = graph.invoke(state)

print(result["profile"])