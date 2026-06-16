import datetime
import json
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any

__all__ = ["PublishCreate", "PublishResponse", "PublishListResponse"]


class PublishCreate(BaseModel):
    model_id: int
    service_type: str = Field(default="api", pattern="^(api|export)$")
    config: dict[str, Any] = Field(default_factory=dict)


class PublishResponse(BaseModel):
    id: int
    model_id: int
    service_type: str
    endpoint: Optional[str] = None
    export_path: Optional[str] = None
    config: dict[str, Any]
    status: str
    pid: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime.datetime
    stopped_at: Optional[datetime.datetime] = None

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


class PublishListResponse(BaseModel):
    services: list[PublishResponse]
    total: int
