import datetime
import json
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any

__all__ = ["TrainingConfig", "TrainingCreate", "TrainingResponse", "TrainingListResponse"]


class TrainingConfig(BaseModel):
    method: str = Field(default="lora", pattern="^(lora|qlora)$")
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 4
    lora_r: int = 8
    lora_alpha: int = 32
    max_length: int = 512
    dataset_path: str = ""
    output_name: str = ""


class TrainingCreate(BaseModel):
    model_id: int
    config: TrainingConfig


class TrainingResponse(BaseModel):
    id: int
    model_id: int
    method: str
    config: dict[str, Any]
    status: str
    pid: Optional[int] = None
    log_path: str
    output_model_id: Optional[int] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

    @field_validator("config", mode="before")
    @classmethod
    def parse_config(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                pass
        return v


class TrainingListResponse(BaseModel):
    tasks: list[TrainingResponse]
    total: int
