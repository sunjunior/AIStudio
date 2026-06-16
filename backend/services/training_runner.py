import asyncio
import json
import os
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from .. import config
from ..database import get_session
from ..models.model_registry import ModelRegistry
from ..models.training_task import TrainingTask


class TrainingRunner:
    """Manage training tasks as subprocesses."""

    def __init__(self):
        self._tasks: dict[int, asyncio.subprocess.Process] = {}

    async def create_and_start(
        self,
        model_id: int,
        method: str,
        training_config: dict,
    ) -> TrainingTask:
        """Create a training task record and start the subprocess."""
        session = get_session()
        try:
            model = session.query(ModelRegistry).filter_by(id=model_id).first()
            if not model:
                raise ValueError(f"Model id={model_id} not found")

            # Capture model fields before session closes
            model_id_val = model.id
            model_name = model.name
            model_source_path = model.source_path
            model_local_path = model.local_path

            task = TrainingTask(
                model_id=model_id,
                method=method,
                config=json.dumps(training_config, ensure_ascii=False),
                status="pending",
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            task_id = task.id
        finally:
            session.remove()

        # Start in background
        asyncio.create_task(self._run_task(
            task_id, model_id_val, model_name, model_source_path, model_local_path, method, training_config
        ))
        return task

    async def _run_task(
        self,
        task_id: int,
        model_id_val: int,
        model_name: str,
        model_source_path: str,
        model_local_path: str,
        method: str,
        config_dict: dict,
    ) -> None:
        """Run the training script as a subprocess."""
        work_dir = Path(config.DATA_DIR) / "training" / str(task_id)
        work_dir.mkdir(parents=True, exist_ok=True)
        log_path = work_dir / "training.log"

        output_name = config_dict.get("output_name", f"{model_name}-lora-{task_id}")

        # Write runtime config
        run_config = {
            "task_id": task_id,
            "base_model": model_source_path or model_local_path,
            "method": method,
            "output_name": output_name,
            "dataset_path": config_dict.get("dataset_path", ""),
            "learning_rate": config_dict.get("learning_rate", config.DEFAULT_LEARNING_RATE),
            "num_epochs": config_dict.get("num_epochs", config.DEFAULT_EPOCHS),
            "batch_size": config_dict.get("batch_size", config.DEFAULT_BATCH_SIZE),
            "lora_r": config_dict.get("lora_r", config.DEFAULT_LORA_R),
            "lora_alpha": config_dict.get("lora_alpha", config.DEFAULT_LORA_ALPHA),
            "max_length": config_dict.get("max_length", config.DEFAULT_MAX_LENGTH),
            "output_dir": str(Path(config.MODELS_DIR) / output_name),
        }
        (work_dir / "config.json").write_text(
            json.dumps(run_config, ensure_ascii=False, indent=2)
        )

        # Update DB: status=running, pid, log_path, started_at
        session = get_session()
        try:
            task = session.query(TrainingTask).filter_by(id=task_id).first()
            task.status = "running"
            task.log_path = str(log_path)
            task.started_at = datetime.utcnow()
            session.commit()
        finally:
            session.remove()

        # Start subprocess
        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", config.TRAINING_SCRIPT,
                str(work_dir / "config.json"),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            self._tasks[task_id] = proc

            # Update PID
            session = get_session()
            try:
                task = session.query(TrainingTask).filter_by(id=task_id).first()
                task.pid = proc.pid
                session.commit()
            finally:
                session.remove()

            # Stream logs
            log_dir = log_path.parent
            log_dir.mkdir(parents=True, exist_ok=True)
            with open(log_path, "wb") as log_file:
                while True:
                    line = await proc.stdout.readline()
                    if not line and proc.returncode is not None:
                        break
                    log_file.write(line)
                    log_file.flush()

            await proc.wait()

            # Check result.json
            result_file = work_dir / "result.json"
            output_model_id = None
            if result_file.exists():
                result = json.loads(result_file.read_text())
                if result.get("status") == "completed" and result.get("output_path"):
                    output_model_id = await self._register_output(
                        output_name, result["output_path"], model_id_val
                    )

            session = get_session()
            try:
                task = session.query(TrainingTask).filter_by(id=task_id).first()
                if proc.returncode == 0 and result_file.exists():
                    result = json.loads(result_file.read_text())
                    if result.get("status") == "completed":
                        task.status = "completed"
                    else:
                        task.status = "failed"
                        task.error_message = result.get("error", "Unknown error")
                elif proc.returncode == -signal.SIGTERM.value:
                    task.status = "cancelled"
                else:
                    task.status = "failed"
                    task.error_message = f"Process exited with code {proc.returncode}"
                task.finished_at = datetime.utcnow()
                task.output_model_id = output_model_id
                session.commit()
            finally:
                session.remove()

        except Exception as exc:
            session = get_session()
            try:
                task = session.query(TrainingTask).filter_by(id=task_id).first()
                task.status = "failed"
                task.error_message = str(exc)
                task.finished_at = datetime.utcnow()
                session.commit()
            finally:
                session.remove()
        finally:
            self._tasks.pop(task_id, None)

    async def _register_output(self, name: str, path: str, base_model_id: int) -> int:
        session = get_session()
        try:
            model = ModelRegistry(
                name=name,
                source="local",
                source_path="",
                model_type="peft_checkpoint",
                base_model_id=base_model_id,
                status="ready",
                local_path=path,
                description=f"LoRA adapter from task training on {base_model_id}",
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return model.id
        finally:
            session.remove()

    def get_task(self, task_id: int) -> Optional[TrainingTask]:
        session = get_session()
        try:
            return session.query(TrainingTask).filter_by(id=task_id).first()
        finally:
            session.remove()

    def list_tasks(self, status: Optional[str] = None) -> list[TrainingTask]:
        session = get_session()
        try:
            query = session.query(TrainingTask)
            if status:
                query = query.filter_by(status=status)
            return query.order_by(TrainingTask.created_at.desc()).all()
        finally:
            session.remove()

    async def cancel_task(self, task_id: int) -> None:
        proc = self._tasks.get(task_id)
        if not proc:
            raise ValueError(f"Task {task_id} is not running")
        try:
            proc.send_signal(signal.SIGTERM)
            try:
                await asyncio.wait_for(proc.wait(), timeout=10)
            except asyncio.TimeoutError:
                proc.send_signal(signal.SIGKILL)
                await proc.wait()
        except ProcessLookupError:
            pass

    def get_task_logs(self, task_id: int, max_lines: int = 500) -> str:
        session = get_session()
        try:
            task = session.query(TrainingTask).filter_by(id=task_id).first()
            if not task or not task.log_path:
                return ""
            log_file = Path(task.log_path)
            if not log_file.exists():
                return ""
            lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
            return "\n".join(lines[-max_lines:])
        finally:
            session.remove()
