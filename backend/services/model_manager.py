import json
import os
import shutil
import threading
from pathlib import Path
from typing import Optional

from huggingface_hub import snapshot_download, HfApi

from .. import config
from ..database import get_session
from ..models.model_registry import ModelRegistry


class ModelManager:
    """Manage model registration, file download, and deletion."""

    def __init__(self):
        self._download_lock = threading.Lock()
        self._download_progress: dict[int, dict] = {}

    def register_model(
        self,
        name: str,
        source: str,
        source_path: str = "",
        model_type: str = "llm",
        base_model_id: Optional[int] = None,
        description: str = "",
    ) -> ModelRegistry:
        """Register a model entry in the database. Does not download files."""
        session = get_session()
        try:
            existing = session.query(ModelRegistry).filter_by(name=name).first()
            if existing:
                raise ValueError(f"Model '{name}' already exists (id={existing.id})")

            local_path = ""
            if source == "local" and source_path:
                local_path = source_path

            model = ModelRegistry(
                name=name,
                source=source,
                source_path=source_path,
                model_type=model_type,
                base_model_id=base_model_id,
                status="ready" if source != "huggingface" else "downloading",
                local_path=local_path,
                description=description,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return model
        finally:
            session.remove()

    def get_model(self, model_id: int) -> Optional[ModelRegistry]:
        session = get_session()
        try:
            return session.query(ModelRegistry).filter_by(id=model_id).first()
        finally:
            session.remove()

    def list_models(
        self,
        model_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[ModelRegistry]:
        session = get_session()
        try:
            query = session.query(ModelRegistry)
            if model_type:
                query = query.filter_by(model_type=model_type)
            if status:
                query = query.filter_by(status=status)
            return query.order_by(ModelRegistry.created_at.desc()).all()
        finally:
            session.remove()

    def delete_model(self, model_id: int) -> None:
        """Delete model record and remove local files if present."""
        session = get_session()
        try:
            model = session.query(ModelRegistry).filter_by(id=model_id).first()
            if not model:
                raise ValueError(f"Model id={model_id} not found")

            # Check for running services referencing this model
            from ..models.published_service import PublishedService
            active = session.query(PublishedService).filter_by(
                model_id=model_id, status="running"
            ).first()
            if active:
                raise ValueError(
                    f"Cannot delete: model has running service (id={active.id}). "
                    "Stop it first."
                )

            # Remove local files
            if model.local_path and os.path.exists(model.local_path):
                shutil.rmtree(model.local_path, ignore_errors=True)

            session.delete(model)
            session.commit()
        finally:
            session.remove()

    def download_model(self, model_id: int) -> None:
        """Download model from HuggingFace in a background thread."""
        session = get_session()
        try:
            model = session.query(ModelRegistry).filter_by(id=model_id).first()
            if not model:
                raise ValueError(f"Model id={model_id} not found")
            if model.source != "huggingface":
                raise ValueError(f"Model source is '{model.source}', not 'huggingface'")
            if not model.source_path:
                raise ValueError("source_path (HF repo ID) is required")

            model.status = "downloading"
            session.commit()
        finally:
            session.remove()

        def _download():
            try:
                target_dir = os.path.join(config.MODELS_DIR, model.name)
                os.makedirs(target_dir, exist_ok=True)

                snapshot_download(
                    repo_id=model.source_path,
                    local_dir=target_dir,
                    cache_dir=config.HF_CACHE_DIR,
                    local_dir_use_symlinks=False,
                    resume_download=True,
                    token=os.environ.get("HF_TOKEN"),
                )

                session = get_session()
                try:
                    m = session.query(ModelRegistry).filter_by(id=model_id).first()
                    m.status = "ready"
                    m.local_path = target_dir
                    session.commit()
                finally:
                    session.remove()
            except Exception as exc:
                session = get_session()
                try:
                    m = session.query(ModelRegistry).filter_by(id=model_id).first()
                    m.status = "error"
                    session.commit()
                finally:
                    session.remove()
                raise

        thread = threading.Thread(target=_download, daemon=True)
        thread.start()

    def get_download_progress(self, model_id: int) -> dict:
        return self._download_progress.get(model_id, {"status": "unknown"})
