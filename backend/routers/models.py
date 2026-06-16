import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import get_session
from ..models.model_registry import ModelRegistry
from ..schemas.model import ModelCreate, ModelResponse, ModelListResponse
from ..services.model_manager import ModelManager

router = APIRouter(prefix="/api/models", tags=["models"])
manager = ModelManager()


@router.get("", response_model=ModelListResponse)
def list_models(
    model_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    models = manager.list_models(model_type=model_type, status=status)
    return ModelListResponse(
        models=[ModelResponse.model_validate(m) for m in models],
        total=len(models),
    )


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int):
    model = manager.get_model(model_id)
    if not model:
        raise HTTPException(404, f"Model id={model_id} not found")
    return ModelResponse.model_validate(model)


@router.post("", response_model=ModelResponse, status_code=201)
def create_model(body: ModelCreate):
    try:
        model = manager.register_model(
            name=body.name,
            source=body.source,
            source_path=body.source_path,
            model_type=body.model_type,
            base_model_id=body.base_model_id,
            description=body.description,
        )
        return ModelResponse.model_validate(model)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{model_id}")
def delete_model(model_id: int):
    try:
        manager.delete_model(model_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{model_id}/download")
def download_model(model_id: int):
    try:
        manager.download_model(model_id)
        return {"status": "downloading"}
    except ValueError as e:
        raise HTTPException(400, str(e))
