import datetime
import json
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any

__all__ = ["EvaluationCreate", "EvaluationResponse", "EvaluationListResponse"]


class EvaluationCreate(BaseModel):
    model_id: int
    eval_type: str = Field(default="perplexity", pattern="^(perplexity|benchmark|custom)$")
    dataset: str = ""


class EvaluationResponse(BaseModel):
    id: int
    model_id: int
    eval_type: str
    dataset: str
    metrics: Optional[Any] = None
    status: str
    log_path: str
    error_message: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

    @field_validator("metrics", mode="before")
    @classmethod
    def parse_metrics(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                pass
        return v


class EvaluationListResponse(BaseModel):
    records: list[EvaluationResponse]
    total: int
