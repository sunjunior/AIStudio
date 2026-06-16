from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..schemas.evaluation import EvaluationCreate, EvaluationResponse, EvaluationListResponse
from ..services.evaluator import Evaluator

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])
evaluator = Evaluator()


@router.post("", response_model=EvaluationResponse, status_code=201)
async def create_evaluation(body: EvaluationCreate):
    try:
        record = await evaluator.create_and_start(
            model_id=body.model_id,
            eval_type=body.eval_type,
            dataset=body.dataset,
        )
        return EvaluationResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("", response_model=EvaluationListResponse)
def list_evaluations(status: Optional[str] = Query(None)):
    records = evaluator.list_records(status=status)
    return EvaluationListResponse(
        records=[EvaluationResponse.model_validate(r) for r in records],
        total=len(records),
    )


@router.get("/{record_id}", response_model=EvaluationResponse)
def get_evaluation(record_id: int):
    record = evaluator.get_record(record_id)
    if not record:
        raise HTTPException(404, f"Record id={record_id} not found")
    return EvaluationResponse.model_validate(record)


@router.delete("/{record_id}")
def delete_evaluation(record_id: int):
    try:
        evaluator.delete_record(record_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{record_id}/logs")
def get_eval_logs(record_id: int):
    logs = evaluator.get_logs(record_id)
    return {"logs": logs}
