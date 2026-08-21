from pydantic import BaseModel


class InsightsOutput(BaseModel):
    summary: str
    key_findings: list[str]
    recommendations: list[str]