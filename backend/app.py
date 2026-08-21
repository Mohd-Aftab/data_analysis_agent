import os
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAIError

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from graph.builder import graph


UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="Agentic Data Analyst API",
    description="FastAPI layer for the existing LangGraph-powered data analysis backend.",
    version="1.0.0",
)

frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
allowed_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")


def _is_csv_upload(upload: UploadFile) -> bool:
    filename = upload.filename or ""
    content_type = upload.content_type or ""
    return filename.lower().endswith(".csv") or content_type in {
        "text/csv",
        "application/vnd.ms-excel",
    }


def _normalize_chart_paths(chart_paths: list[str] | None) -> list[str]:
    normalized: list[str] = []
    for path in chart_paths or []:
        posix_path = Path(path).as_posix()
        if posix_path.startswith("outputs/"):
            normalized.append(f"/{posix_path}")
        else:
            normalized.append(f"/outputs/{Path(path).name}")
    return normalized


def _serialize_model_results(model_results: dict[str, Any] | None) -> dict[str, Any] | None:
    if not model_results:
        return model_results

    serialized: dict[str, Any] = {}
    for model_name, result in model_results.items():
        serialized[model_name] = {
            "metrics": (result or {}).get("metrics")
        }
    return serialized


def _build_response(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent": result.get("intent"),
        "target_column": result.get("target_column"),
        "profile": result.get("profile"),
        "preprocessing_plan": result.get("preprocessing_plan"),
        "preprocessing_summary": result.get("preprocessing_summary"),
        "eda_plan": result.get("eda_plan"),
        "eda_result": result.get("eda_result"),
        "feature_engineering_plan": result.get("feature_engineering_plan"),
        "model_results": _serialize_model_results(result.get("model_results")),
        "best_model": result.get("best_model"),
        "model_metrics": result.get("model_metrics"),
        "visualization_plan": result.get("visualization_plan"),
        "chart_paths": _normalize_chart_paths(result.get("chart_paths")),
        "insights": result.get("insights"),
        "error": result.get("error"),
    }


@app.get("/")
def get_started() -> dict[str, str]:
    return {"message": "Welcome to the Agentic Data Analyst API."}


@app.post("/api/analyze")
async def analyze_dataset(
    file: UploadFile = File(...),
    user_query: str = Form(...),
) -> dict[str, Any]:
    if not user_query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User query is required.",
        )

    if not _is_csv_upload(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV uploads are supported.",
        )

    file_name = file.filename or "dataset.csv"
    file_extension = Path(file_name).suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{file_extension or '.csv'}"
    stored_path = UPLOADS_DIR / stored_name

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        stored_path.write_bytes(contents)

        initial_state = {
            "user_query": user_query.strip(),
            "intent": None,
            "uploaded_file_path": str(stored_path),
            "dataframe": None,
            "profile": None,
        }

        result = graph.invoke(initial_state)
        response = _build_response(result)

        if response.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response["error"],
            )

        return response

    except HTTPException:
        raise
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM provider error: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {exc}",
        ) from exc
    finally:
        await file.close()

