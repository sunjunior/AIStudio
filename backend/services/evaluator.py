import asyncio
import json
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional

from .. import config
from ..database import get_session
from ..models.model_registry import ModelRegistry
from ..models.evaluation_record import EvaluationRecord


class Evaluator:
    """Manage evaluation tasks as subprocesses."""

    def __init__(self):
        self._tasks: dict[int, asyncio.subprocess.Process] = {}

    async def create_and_start(
        self,
        model_id: int,
        eval_type: str,
        dataset: str = "",
    ) -> EvaluationRecord:
        session = get_session()
        try:
            model = session.query(ModelRegistry).filter_by(id=model_id).first()
            if not model:
                raise ValueError(f"Model id={model_id} not found")

            # Capture fields before session closes
            model_path = model.local_path or model.source_path
            model_type_name = model.model_type

            record = EvaluationRecord(
                model_id=model_id,
                eval_type=eval_type,
                dataset=dataset,
                status="pending",
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            record_id = record.id
        finally:
            session.remove()

        asyncio.create_task(self._run_eval(record_id, model_path, model_type_name, eval_type, dataset))
        return record

    async def _run_eval(
        self,
        record_id: int,
        model_path: str,
        model_type_name: str,
        eval_type: str,
        dataset: str,
    ) -> None:
        work_dir = Path(config.DATA_DIR) / "evaluation" / str(record_id)
        work_dir.mkdir(parents=True, exist_ok=True)
        log_path = work_dir / "eval.log"

        run_config = {
            "record_id": record_id,
            "model_path": model_path,
            "model_type": model_type_name,
            "eval_type": eval_type,
            "dataset": dataset,
        }
        (work_dir / "config.json").write_text(
            json.dumps(run_config, ensure_ascii=False, indent=2)
        )

        session = get_session()
        try:
            rec = session.query(EvaluationRecord).filter_by(id=record_id).first()
            rec.status = "running"
            rec.log_path = str(log_path)
            session.commit()
        finally:
            session.remove()

        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", config.EVAL_SCRIPT,
                str(work_dir / "config.json"),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            self._tasks[record_id] = proc

            with open(log_path, "wb") as log_file:
                while True:
                    line = await proc.stdout.readline()
                    if not line and proc.returncode is not None:
                        break
                    log_file.write(line)
                    log_file.flush()

            await proc.wait()

            result_file = work_dir / "result.json"
            metrics = None
            error_msg = None
            if result_file.exists():
                result = json.loads(result_file.read_text())
                metrics = result.get("metrics")
                error_msg = result.get("error")

            session = get_session()
            try:
                rec = session.query(EvaluationRecord).filter_by(id=record_id).first()
                if proc.returncode == 0 and metrics is not None:
                    rec.status = "completed"
                    rec.metrics = json.dumps(metrics, ensure_ascii=False)
                else:
                    rec.status = "failed"
                    rec.error_message = error_msg or f"Exit code {proc.returncode}"
                session.commit()
            finally:
                session.remove()

        except Exception as exc:
            session = get_session()
            try:
                rec = session.query(EvaluationRecord).filter_by(id=record_id).first()
                rec.status = "failed"
                rec.error_message = str(exc)
                session.commit()
            finally:
                session.remove()
        finally:
            self._tasks.pop(record_id, None)

    def get_record(self, record_id: int) -> Optional[EvaluationRecord]:
        session = get_session()
        try:
            return session.query(EvaluationRecord).filter_by(id=record_id).first()
        finally:
            session.remove()

    def list_records(self, status: Optional[str] = None) -> list[EvaluationRecord]:
        session = get_session()
        try:
            query = session.query(EvaluationRecord)
            if status:
                query = query.filter_by(status=status)
            return query.order_by(EvaluationRecord.created_at.desc()).all()
        finally:
            session.remove()

    def delete_record(self, record_id: int) -> None:
        session = get_session()
        try:
            rec = session.query(EvaluationRecord).filter_by(id=record_id).first()
            if not rec:
                raise ValueError(f"Record id={record_id} not found")
            session.delete(rec)
            session.commit()
        finally:
            session.remove()

    def get_logs(self, record_id: int, max_lines: int = 500) -> str:
        session = get_session()
        try:
            rec = session.query(EvaluationRecord).filter_by(id=record_id).first()
            if not rec or not rec.log_path:
                return ""
            log_file = Path(rec.log_path)
            if not log_file.exists():
                return ""
            lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
            return "\n".join(lines[-max_lines:])
        finally:
            session.remove()
