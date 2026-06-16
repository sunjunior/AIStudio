import datetime
from pydantic import BaseModel, Field
from typing import Optional

__all__ = ["ModelCreate", "ModelResponse", "ModelListResponse"]


class ModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source: str = Field(default="huggingface", pattern="^(huggingface|local|uploaded)$")
    source_path: str = ""
    model_type: str = Field(default="llm", pattern="^(llm|embedding|peft_checkpoint)$")
    base_model_id: Optional[int] = None
    description: str = ""


class ModelResponse(BaseModel):
    id: int
    name: str
    source: str
    source_path: str
    model_type: str
    base_model_id: Optional[int] = None
    status: str
    local_path: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    models: list[ModelResponse]
    total: int
