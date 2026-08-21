from tools.csv_tool import load_csv
from tools.profiling_tool import profile_dataframe


def profiling_node(state):

    df = load_csv(state["uploaded_file_path"])

    profile = profile_dataframe(df)

    observations = []

    observations.append(
        f"Dataset contains {profile['rows']} rows and {profile['columns']} columns."
    )

    if profile["duplicates"] > 0:
        observations.append(
            f"{profile['duplicates']} duplicate rows detected."
        )

    else:
        observations.append(
            "No duplicate rows found."
        )

    if any(profile["missing_values"].values()):
        observations.append(
            "Missing values detected."
        )
    else:
        observations.append(
            "No missing values detected."
        )

    return {
        "dataframe": df,
        "profile": profile,
        "preprocessing_summary": observations
    }