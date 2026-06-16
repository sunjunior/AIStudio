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
from ..models.published_service import PublishedService


class Publisher:
    """Manage model publishing (API service or export)."""

    def __init__(self):
        self._services: dict[int, asyncio.subprocess.Process] = {}

    async def publish(
        self,
        model_id: int,
        service_type: str,
        publish_config: dict,
    ) -> PublishedService:
        session = get_session()
        try:
            model = session.query(ModelRegistry).filter_by(id=model_id).first()
            if not model:
                raise ValueError(f"Model id={model_id} not found")

            service = PublishedService(
                model_id=model_id,
                service_type=service_type,
                config=json.dumps(publish_config, ensure_ascii=False),
                status="stopped",
            )
            session.add(service)
            session.commit()
            session.refresh(service)
            service_id = service.id
        finally:
            session.remove()

        if service_type == "api":
            asyncio.create_task(self._start_api_service(service_id, model, publish_config))

        return service

    async def _start_api_service(
        self,
        service_id: int,
        model: ModelRegistry,
        service_config: dict,
    ) -> None:
        port = service_config.get("port", 8300)
        host = service_config.get("host", "127.0.0.1")
        model_path = model.local_path or model.source_path

        session = get_session()
        try:
            service = session.query(PublishedService).filter_by(id=service_id).first()
            service.endpoint = f"http://{host}:{port}"
            service.status = "running"
            session.commit()
        finally:
            session.remove()

        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", config.API_SERVER_SCRIPT,
                "--model_path", model_path,
                "--model_type", model.model_type,
                "--host", host,
                "--port", str(port),
                "--service_id", str(service_id),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            self._services[service_id] = proc

            session = get_session()
            try:
                service = session.query(PublishedService).filter_by(id=service_id).first()
                service.pid = proc.pid
                session.commit()
            finally:
                session.remove()

            # Wait for process to exit
            await proc.wait()

            session = get_session()
            try:
                service = session.query(PublishedService).filter_by(id=service_id).first()
                if service and service.status != "stopped":
                    service.status = "failed"
                    service.error_message = f"Process exited with code {proc.returncode}"
                    session.commit()
            finally:
                session.remove()

        except Exception as exc:
            session = get_session()
            try:
                service = session.query(PublishedService).filter_by(id=service_id).first()
                service.status = "failed"
                service.error_message = str(exc)
                session.commit()
            finally:
                session.remove()
        finally:
            self._services.pop(service_id, None)

    async def publish_export(
        self,
        model_id: int,
        export_path: str,
    ) -> PublishedService:
        session = get_session()
        try:
            model = session.query(ModelRegistry).filter_by(id=model_id).first()
            if not model:
                raise ValueError(f"Model id={model_id} not found")

            if model.model_type == "peft_checkpoint" and model.base_model_id:
                base = session.query(ModelRegistry).filter_by(id=model.base_model_id).first()
                if not base:
                    raise ValueError("Base model not found")
                merged_path = self._merge_peft(base, model, export_path)
            else:
                merged_path = self._copy_model(model, export_path)

            service = PublishedService(
                model_id=model_id,
                service_type="export",
                config=json.dumps({"export_path": export_path}),
                status="stopped",
                export_path=merged_path,
            )
            session.add(service)
            session.commit()
            session.refresh(service)
            return service
        finally:
            session.remove()

    def _merge_peft(self, base_model: ModelRegistry, adapter: ModelRegistry, export_path: str) -> str:
        Path(export_path).mkdir(parents=True, exist_ok=True)
        info = {
            "base_model": base_model.local_path or base_model.source_path,
            "adapter": adapter.local_path,
            "merged_at": datetime.utcnow().isoformat(),
        }
        (Path(export_path) / "export_info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2)
        )
        return export_path

    def _copy_model(self, model: ModelRegistry, export_path: str) -> str:
        import shutil
        src = Path(model.local_path)
        dst = Path(export_path)
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.mkdir(parents=True, exist_ok=True)
        return export_path

    async def stop_service(self, service_id: int) -> None:
        session = get_session()
        try:
            service = session.query(PublishedService).filter_by(id=service_id).first()
            if not service:
                raise ValueError(f"Service id={service_id} not found")
            if service.status != "running":
                raise ValueError(f"Service is not running (status={service.status})")
        finally:
            session.remove()

        proc = self._services.get(service_id)
        if proc:
            try:
                proc.send_signal(signal.SIGTERM)
                try:
                    await asyncio.wait_for(proc.wait(), timeout=10)
                except asyncio.TimeoutError:
                    proc.send_signal(signal.SIGKILL)
            except ProcessLookupError:
                pass

        session = get_session()
        try:
            service = session.query(PublishedService).filter_by(id=service_id).first()
            service.status = "stopped"
            service.stopped_at = datetime.utcnow()
            session.commit()
        finally:
            session.remove()

    def get_service(self, service_id: int) -> Optional[PublishedService]:
        session = get_session()
        try:
            return session.query(PublishedService).filter_by(id=service_id).first()
        finally:
            session.remove()

    def list_services(self) -> list[PublishedService]:
        session = get_session()
        try:
            return session.query(PublishedService).order_by(
                PublishedService.created_at.desc()
            ).all()
        finally:
            session.remove()

    async def delete_service(self, service_id: int) -> None:
        session = get_session()
        try:
            service = session.query(PublishedService).filter_by(id=service_id).first()
            if not service:
                raise ValueError(f"Service id={service_id} not found")
            if service.status == "running":
                await self.stop_service(service_id)
            session.delete(service)
            session.commit()
        finally:
            session.remove()
