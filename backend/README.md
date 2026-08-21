# Agentic Data Analyst

An LLM-driven data analysis system built with **LangGraph, LangChain, OpenAI, Pandas, and Scikit-learn**.

The system accepts a user's natural-language analysis request and dynamically plans and executes the required data-analysis workflow using specialized agents and deterministic Python tools.

## 🚀 Capabilities

- **Dataset Profiling**
  - Data types
  - Missing values
  - Duplicate detection
  - Dataset statistics

- **LLM-driven Preprocessing**
  - Numeric type conversion
  - Missing-value handling
  - Duplicate removal
  - Constant-column removal

- **Exploratory Data Analysis**
  - Numerical summaries
  - Categorical analysis
  - Outlier detection
  - Correlation analysis
  - Feature-target relationships

- **Feature Engineering**
  - Log transformations
  - Numerical binning
  - Rare-category handling
  - Ratio features
  - Interaction features

- **Machine Learning**
  - Automatic classification/regression detection
  - Candidate model selection
  - Model comparison
  - Best-model selection
  - Classification and regression metrics

- **LLM-driven Visualization**
  - Target distributions
  - Numerical distributions
  - Categorical distributions
  - Correlation heatmaps
  - Feature-target visualizations

- **AI-generated Insights**
  - Key findings
  - Model interpretation
  - Practical recommendations

---

## 🧠 Architecture

```text
                         User Query
                             │
                             ▼
                      ┌─────────────┐
                      │ LLM Planner │
                      └──────┬──────┘
                             │
                     Conditional Routing
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
        EDA / Analysis                 Prediction
              │                             │
              ▼                             ▼
        EDA Agent                    Preprocessing
              │                             │
              ▼                             ▼
     Visualization Agent           Feature Engineering
              │                             │
              │                             ▼
              │                             ML Agent
              │                             │
              └──────────────┬──────────────┘
                             ▼
                     Insights Agent
                             │
                             ▼
                       Final Output
```

## 🔑 Design Philosophy

The system follows a simple principle:

> **LLM decides, deterministic tools execute.**

The LLM is responsible for planning and selecting appropriate operations.

Python tools perform the actual:

- data manipulation
- statistical calculations
- visualization
- model training
- model evaluation

The LLM does **not** directly execute arbitrary Python code.

This improves reliability and makes the system easier to validate and debug.

## 🛡️ Hallucination Control

The system uses several mechanisms to reduce unreliable LLM behavior:

- Structured outputs using **Pydantic**
- Restricted action/model choices using `Literal`
- Dataset-aware planning using profiling information
- Validation of selected columns before tool execution
- Deterministic Python tools for calculations
- Scikit-learn for model training and evaluation
- LLM used primarily for planning and interpretation rather than numerical computation

For example:

```text
LLM
 ↓
"correlation_analysis"
 ↓
Python EDA tool
 ↓
Actual correlation calculation
```

rather than asking the LLM to calculate the correlation itself.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| LangGraph | Agent orchestration |
| LangChain | LLM integration |
| OpenAI | LLM reasoning/planning |
| Pydantic | Structured outputs |
| Pandas | Data processing |
| Scikit-learn | Machine learning |
| Matplotlib / Seaborn | Visualization |
| FastAPI | API layer |

---

## 📁 Project Structure

```text
backend/
│
├── app.py
│
├── graph/
│   ├── builder.py
│   ├── state.py
│   └── edges.py
│
├── agents/
│   ├── planner.py
│   ├── profiling.py
│   ├── preprocessing.py
│   ├── eda.py
│   ├── feature_engineering.py
│   ├── ml.py
│   ├── visualization.py
│   ├── insights.py
│   └── error.py
│
├── tools/
│   ├── pandas_tool.py
│   ├── eda_tool.py
│   ├── feature_engineering_tool.py
│   ├── sklearn_tool.py
│   ├── plot_tool.py
│   └── report_tool.py
│
├── schemas/
│   ├── planner_schema.py
│   ├── eda.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   └── visualization.py
│
├── utils/
│
├── uploads/
│
└── requirements.txt
```

---

## 🔄 Example Workflow

User:

> **"Prepare this dataset for churn prediction, create useful features, and build a prediction model."**

The system can execute:

```text
Profiling
    ↓
LLM Planner
    ↓
Preprocessing
    ↓
Feature Engineering
    ↓
ML Planner
    ↓
Candidate Models
    ↓
Model Comparison
    ↓
Best Model
    ↓
LLM Insights
```

For an analysis-focused request:

```text
Profiling
    ↓
LLM Planner
    ↓
EDA
    ↓
Visualization
    ↓
LLM Insights
```

---

## 🎯 Future Improvements

The current project intentionally focuses on a practical MVP.

Potential future improvements include:

- Persistent dataset storage using S3/database
- Agent memory
- More sophisticated multi-agent collaboration
- Human-in-the-loop approval
- Model explainability using SHAP
- Experiment tracking
- Production deployment
- More advanced feature engineering
- Automated report generation

---

## ⚠️ Scope

This project is designed as a **resume-grade Agentic AI MVP**, not as a production replacement for a full data science team.

The architecture prioritizes:

- clear agent orchestration
- controlled tool execution
- explainability
- deterministic data/ML operations
- practical LLM usage
