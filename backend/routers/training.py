from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..schemas.training import TrainingCreate, TrainingResponse, TrainingListResponse
from ..services.training_runner import TrainingRunner

router = APIRouter(prefix="/api/training", tags=["training"])
runner = TrainingRunner()


@router.post("", response_model=TrainingResponse, status_code=201)
async def create_training(body: TrainingCreate):
    try:
        task = await runner.create_and_start(
            model_id=body.model_id,
            method=body.config.method,
            training_config=body.config.model_dump(),
        )
        return TrainingResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("", response_model=TrainingListResponse)
def list_tasks(status: Optional[str] = Query(None)):
    tasks = runner.list_tasks(status=status)
    return TrainingListResponse(
        tasks=[TrainingResponse.model_validate(t) for t in tasks],
        total=len(tasks),
    )


@router.get("/{task_id}", response_model=TrainingResponse)
def get_task(task_id: int):
    task = runner.get_task(task_id)
    if not task:
        raise HTTPException(404, f"Task id={task_id} not found")
    return TrainingResponse.model_validate(task)


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: int):
    try:
        await runner.cancel_task(task_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{task_id}/logs")
def get_logs(task_id: int):
    logs = runner.get_task_logs(task_id)
    return {"logs": logs}
