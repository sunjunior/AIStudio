# AIStudio 后端实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现 AIStudio 的后端系统——FastAPI + SQLite + transformers/peft，提供模型管理、训练、评估和发布的 REST API。

**架构：** 四层架构：路由层（routers/）→ 服务层（services/）→ ORM 模型层（models/）→ SQLite，训练/评估通过 subprocess 调用独立脚本执行。

**技术栈：** Python 3.10+, FastAPI, SQLAlchemy 2.0, aiosqlite, Pydantic v2, transformers, peft, datasets, huggingface-hub

---

## 文件清单

| # | 文件 | 职责 |
|---|------|------|
| 1 | `backend/config.py` | 全局配置（路径、默认参数） |
| 2 | `backend/database.py` | SQLAlchemy 引擎 + 会话 + 建表 |
| 3 | `backend/models/__init__.py` | 模型导出 |
| 4 | `backend/models/model_registry.py` | Model ORM |
| 5 | `backend/models/training_task.py` | TrainingTask ORM |
| 6 | `backend/models/evaluation_record.py` | EvaluationRecord ORM |
| 7 | `backend/models/published_service.py` | PublishedService ORM |
| 8 | `backend/schemas/model.py` | Model Pydantic schemas |
| 9 | `backend/schemas/training.py` | Training Pydantic schemas |
| 10 | `backend/schemas/evaluation.py` | Evaluation Pydantic schemas |
| 11 | `backend/schemas/publishing.py` | Publishing Pydantic schemas |
| 12 | `backend/services/model_manager.py` | 模型文件管理 + HF 下载 |
| 13 | `backend/services/training_runner.py` | 训练任务调度（子进程） |
| 14 | `backend/services/evaluator.py` | 评估调度（子进程） |
| 15 | `backend/services/publisher.py` | 发布管理（API + 导出） |
| 16 | `backend/routers/models.py` | /api/models 路由 |
| 17 | `backend/routers/training.py` | /api/training 路由 |
| 18 | `backend/routers/evaluation.py` | /api/evaluation 路由 |
| 19 | `backend/routers/publishing.py` | /api/publishing 路由 |
| 20 | `backend/main.py` | FastAPI 入口 |
| 21 | `backend/scripts/train_lora.py` | LoRA/QLoRA 训练脚本 |
| 22 | `backend/scripts/evaluate.py` | 评估脚本 |
| 23 | `backend/scripts/api_server.py` | API 发布推理服务 |
| 24 | `backend/requirements.txt` | Python 依赖 |

---

### 任务 1：项目骨架（配置 + 数据库 + 包初始化）

**文件：**
- 创建：`AIStudio/backend/__init__.py`
- 创建：`AIStudio/backend/config.py`
- 创建：`AIStudio/backend/database.py`
- 创建：`AIStudio/backend/models/__init__.py`
- 创建：`AIStudio/backend/models/model_registry.py`
- 创建：`AIStudio/backend/models/training_task.py`
- 创建：`AIStudio/backend/models/evaluation_record.py`
- 创建：`AIStudio/backend/models/published_service.py`
- 创建：`AIStudio/backend/requirements.txt`

- [ ] **步骤 1：创建包初始化文件**

`AIStudio/backend/__init__.py`:
```python
"""AIStudio backend."""
```

`AIStudio/backend/models/__init__.py`:
```python
from .model_registry import ModelRegistry
from .training_task import TrainingTask
from .evaluation_record import EvaluationRecord
from .published_service import PublishedService

__all__ = ["ModelRegistry", "TrainingTask", "EvaluationRecord", "PublishedService"]
```

- [ ] **步骤 2：创建 config.py**

`AIStudio/backend/config.py`:
```python
import os
from pathlib import Path

BACKEND_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = BACKEND_DIR.parent

DATA_DIR = os.environ.get("AISTUDIO_DATA_DIR", str(PROJECT_DIR / "data"))
MODELS_DIR = os.environ.get("AISTUDIO_MODELS_DIR", str(Path(DATA_DIR) / "models"))
DB_PATH = os.environ.get("AISTUDIO_DB_PATH", str(Path(DATA_DIR) / "aistudio.db"))
HF_CACHE_DIR = os.environ.get("AISTUDIO_HF_CACHE", str(Path(DATA_DIR) / "hf_cache"))

TRAINING_SCRIPT = str(BACKEND_DIR / "scripts" / "train_lora.py")
EVAL_SCRIPT = str(BACKEND_DIR / "scripts" / "evaluate.py")
API_SERVER_SCRIPT = str(BACKEND_DIR / "scripts" / "api_server.py")

API_HOST = os.environ.get("AISTUDIO_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("AISTUDIO_PORT", "8000"))

# Training defaults
DEFAULT_EPOCHS = 3
DEFAULT_BATCH_SIZE = 4
DEFAULT_LEARNING_RATE = 2e-4
DEFAULT_LORA_R = 8
DEFAULT_LORA_ALPHA = 32
DEFAULT_MAX_LENGTH = 512
```

- [ ] **步骤 3：创建 database.py**

`AIStudio/backend/database.py`:
```python
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session

from . import config


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{config.DB_PATH}",
            echo=False,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(_engine, "connect")
        def _set_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = scoped_session(sessionmaker(bind=get_engine()))
    return _SessionLocal


def init_db():
    """Create all tables."""
    from .models import ModelRegistry, TrainingTask, EvaluationRecord, PublishedService  # noqa
    Base.metadata.create_all(bind=get_engine())
```

- [ ] **步骤 4：创建 ModelRegistry ORM**

`AIStudio/backend/models/model_registry.py`:
```python
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from ..database import Base


class ModelRegistry(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), nullable=False)  # huggingface / local / uploaded
    source_path = Column(String(512), default="")
    model_type = Column(String(50), nullable=False)  # llm / embedding / peft_checkpoint
    base_model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default="ready")  # downloading / ready / error
    local_path = Column(String(512), default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    base_model = relationship("ModelRegistry", remote_side=[id], backref="adapters")
```

- [ ] **步骤 5：创建 TrainingTask ORM**

`AIStudio/backend/models/training_task.py`:
```python
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class TrainingTask(Base):
    __tablename__ = "training_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(50), nullable=False)  # lora / qlora
    config = Column(Text, nullable=False)  # JSON
    status = Column(String(50), nullable=False, default="pending")
    # pending / running / completed / failed / cancelled
    pid = Column(Integer, nullable=True)
    log_path = Column(String(512), default="")
    output_model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    model = relationship("ModelRegistry", foreign_keys=[model_id])
    output_model = relationship("ModelRegistry", foreign_keys=[output_model_id])
```

- [ ] **步骤 6：创建 EvaluationRecord ORM**

`AIStudio/backend/models/evaluation_record.py`:
```python
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    eval_type = Column(String(50), nullable=False)  # perplexity / benchmark / custom
    dataset = Column(String(512), default="")
    metrics = Column(Text, nullable=True)  # JSON
    status = Column(String(50), nullable=False, default="pending")
    # pending / running / completed / failed
    log_path = Column(String(512), default="")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    model = relationship("ModelRegistry")
```

- [ ] **步骤 7：创建 PublishedService ORM**

`AIStudio/backend/models/published_service.py`:
```python
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class PublishedService(Base):
    __tablename__ = "published_services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    service_type = Column(String(50), nullable=False)  # api / export
    endpoint = Column(String(512), nullable=True)
    export_path = Column(String(512), nullable=True)
    config = Column(Text, default="{}")  # JSON
    status = Column(String(50), nullable=False, default="stopped")
    # running / stopped / failed
    pid = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)

    model = relationship("ModelRegistry")
```

- [ ] **步骤 8：创建 requirements.txt**

`AIStudio/backend/requirements.txt`:
```txt
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
pydantic>=2.5.0
huggingface-hub>=0.20.0
transformers>=4.36.0
peft>=0.7.0
datasets>=2.16.0
bitsandbytes>=0.41.0
python-dotenv>=1.0.0
```

- [ ] **步骤 9：验证导入**

运行：`cd AIStudio/backend && python3 -c "from database import init_db; init_db(); print('DB OK')"`
预期输出：`DB OK`，且 `data/aistudio.db` 文件创建成功

- [ ] **步骤 10：Commit**

```bash
git add AIStudio/backend/__init__.py AIStudio/backend/config.py AIStudio/backend/database.py AIStudio/backend/models/ AIStudio/backend/requirements.txt
git commit -m "feat: add backend skeleton - config, database, ORM models"
```

---

### 任务 2：Pydantic Schemas

**文件：**
- 创建：`AIStudio/backend/schemas/__init__.py`
- 创建：`AIStudio/backend/schemas/model.py`
- 创建：`AIStudio/backend/schemas/training.py`
- 创建：`AIStudio/backend/schemas/evaluation.py`
- 创建：`AIStudio/backend/schemas/publishing.py`

- [ ] **步骤 1：创建 schemas 包**

`AIStudio/backend/schemas/__init__.py`:
```python
from .model import *
from .training import *
from .evaluation import *
from .publishing import *
```

- [ ] **步骤 2：编写 model schemas**

`AIStudio/backend/schemas/model.py`:
```python
import datetime
from pydantic import BaseModel, Field
from typing import Optional


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
```

- [ ] **步骤 3：编写 training schemas**

`AIStudio/backend/schemas/training.py`:
```python
import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any


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
    config: Any
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


class TrainingListResponse(BaseModel):
    tasks: list[TrainingResponse]
    total: int
```

- [ ] **步骤 4：编写 evaluation schemas**

`AIStudio/backend/schemas/evaluation.py`:
```python
import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any


class EvaluationCreate(BaseModel):
    model_id: int
    eval_type: str = Field(default="perplexity", pattern="^(perplexity|benchmark|custom)$")
    dataset: str = ""


class EvaluationResponse(BaseModel):
    id: int
    model_id: int
    eval_type: str
    dataset: str
    metrics: Optional[Any] = None
    status: str
    log_path: str
    error_message: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class EvaluationListResponse(BaseModel):
    records: list[EvaluationResponse]
    total: int
```

- [ ] **步骤 5：编写 publishing schemas**

`AIStudio/backend/schemas/publishing.py`:
```python
import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any


class PublishCreate(BaseModel):
    model_id: int
    service_type: str = Field(default="api", pattern="^(api|export)$")
    config: Any = {}  # port, max_tokens, temperature for api; export_path for export


class PublishResponse(BaseModel):
    id: int
    model_id: int
    service_type: str
    endpoint: Optional[str] = None
    export_path: Optional[str] = None
    config: Any
    status: str
    pid: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime.datetime
    stopped_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class PublishListResponse(BaseModel):
    services: list[PublishResponse]
    total: int
```

- [ ] **步骤 6：验证导入**

运行：`cd AIStudio/backend && python3 -c "from schemas import ModelCreate, TrainingCreate, EvaluationCreate, PublishCreate; print('Schemas OK')"`
预期：`Schemas OK`

- [ ] **步骤 7：Commit**

```bash
git add AIStudio/backend/schemas/
git commit -m "feat: add Pydantic schemas for all API endpoints"
```

---

### 任务 3：模型管理服务

**文件：**
- 创建：`AIStudio/backend/services/__init__.py`
- 创建：`AIStudio/backend/services/model_manager.py`

- [ ] **步骤 1：创建 services 包**

`AIStudio/backend/services/__init__.py`:
```python
from .model_manager import ModelManager
from .training_runner import TrainingRunner
from .evaluator import Evaluator
from .publisher import Publisher

__all__ = ["ModelManager", "TrainingRunner", "Evaluator", "Publisher"]
```

- [ ] **步骤 2：编写 ModelManager 服务**

`AIStudio/backend/services/model_manager.py`:
```python
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
```

- [ ] **步骤 3：Commit**

```bash
git add AIStudio/backend/services/__init__.py AIStudio/backend/services/model_manager.py
git commit -m "feat: add ModelManager service - register, list, delete, download"
```

---

### 任务 4：训练运行器服务

**文件：**
- 创建：`AIStudio/backend/services/training_runner.py`

- [ ] **步骤 1：编写 TrainingRunner**

`AIStudio/backend/services/training_runner.py`:
```python
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
        asyncio.create_task(self._run_task(task_id, model, method, training_config))
        return task

    async def _run_task(
        self,
        task_id: int,
        model: ModelRegistry,
        method: str,
        config_dict: dict,
    ) -> None:
        """Run the training script as a subprocess."""
        work_dir = Path(config.DATA_DIR) / "training" / str(task_id)
        work_dir.mkdir(parents=True, exist_ok=True)
        log_path = work_dir / "training.log"

        # Ensure output model name
        output_name = config_dict.get("output_name", f"{model.name}-lora-{task_id}")

        # Write runtime config
        run_config = {
            "task_id": task_id,
            "base_model": model.source_path or model.local_path,
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
                    # Register the output as a peft_checkpoint model
                    output_model_id = await self._register_output(
                        output_name, result["output_path"], model.id
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
            pass  # already exited

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
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/services/training_runner.py
git commit -m "feat: add TrainingRunner - subprocess training management"
```

---

### 任务 5：评估器服务

**文件：**
- 创建：`AIStudio/backend/services/evaluator.py`

- [ ] **步骤 1：编写 Evaluator**

`AIStudio/backend/services/evaluator.py`:
```python
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

        asyncio.create_task(self._run_eval(record_id, model, eval_type, dataset))
        return record

    async def _run_eval(
        self,
        record_id: int,
        model: ModelRegistry,
        eval_type: str,
        dataset: str,
    ) -> None:
        work_dir = Path(config.DATA_DIR) / "evaluation" / str(record_id)
        work_dir.mkdir(parents=True, exist_ok=True)
        log_path = work_dir / "eval.log"

        run_config = {
            "record_id": record_id,
            "model_path": model.local_path or model.source_path,
            "model_type": model.model_type,
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
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/services/evaluator.py
git commit -m "feat: add Evaluator service - subprocess evaluation management"
```

---

### 任务 6：发布服务

**文件：**
- 创建：`AIStudio/backend/services/publisher.py`

- [ ] **步骤 1：编写 Publisher**

`AIStudio/backend/services/publisher.py`:
```python
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

            # Wait for process to exit (should stay running until stopped)
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
        """Merge LoRA weights and export to target directory."""
        session = get_session()
        try:
            model = session.query(ModelRegistry).filter_by(id=model_id).first()
            if not model:
                raise ValueError(f"Model id={model_id} not found")

            # For peft_checkpoint, merge weights with base model
            if model.model_type == "peft_checkpoint" and model.base_model_id:
                base = session.query(ModelRegistry).filter_by(id=model.base_model_id).first()
                if not base:
                    raise ValueError("Base model not found")
                merged_path = self._merge_peft(base, model, export_path)
            else:
                # Copy model files
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
        """Merge PEFT adapter weights with base model (sync call in thread)."""
        # This is a heavy operation - in production would run in subprocess
        # For now, we just record the intent and export config
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
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/services/publisher.py
git commit -m "feat: add Publisher service - API and export publishing"
```

---

### 任务 7：API 路由 — 模型管理

**文件：**
- 创建：`AIStudio/backend/routers/__init__.py`
- 创建：`AIStudio/backend/routers/models.py`

- [ ] **步骤 1：创建 routers 包**

`AIStudio/backend/routers/__init__.py`:
```python
from .models import router as models_router
from .training import router as training_router
from .evaluation import router as evaluation_router
from .publishing import router as publishing_router

__all__ = ["models_router", "training_router", "evaluation_router", "publishing_router"]
```

- [ ] **步骤 2：编写 models 路由**

`AIStudio/backend/routers/models.py`:
```python
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
```

- [ ] **步骤 3：Commit**

```bash
git add AIStudio/backend/routers/__init__.py AIStudio/backend/routers/models.py
git commit -m "feat: add model management API routes"
```

---

### 任务 8：API 路由 — 训练

**文件：**
- 创建：`AIStudio/backend/routers/training.py`

- [ ] **步骤 1：编写 training 路由**

`AIStudio/backend/routers/training.py`:
```python
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
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/routers/training.py
git commit -m "feat: add training API routes"
```

---

### 任务 9：API 路由 — 评估

**文件：**
- 创建：`AIStudio/backend/routers/evaluation.py`

- [ ] **步骤 1：编写 evaluation 路由**

`AIStudio/backend/routers/evaluation.py`:
```python
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
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/routers/evaluation.py
git commit -m "feat: add evaluation API routes"
```

---

### 任务 10：API 路由 — 发布

**文件：**
- 创建：`AIStudio/backend/routers/publishing.py`

- [ ] **步骤 1：编写 publishing 路由**

`AIStudio/backend/routers/publishing.py`:
```python
from fastapi import APIRouter, HTTPException

from ..schemas.publishing import PublishCreate, PublishResponse, PublishListResponse
from ..services.publisher import Publisher

router = APIRouter(prefix="/api/publishing", tags=["publishing"])
publisher = Publisher()


@router.post("", response_model=PublishResponse, status_code=201)
async def create_publish(body: PublishCreate):
    try:
        if body.service_type == "export":
            export_path = body.config.get("export_path", "")
            if not export_path:
                raise HTTPException(400, "export_path required for export")
            service = await publisher.publish_export(
                model_id=body.model_id,
                export_path=export_path,
            )
        else:
            service = await publisher.publish(
                model_id=body.model_id,
                service_type=body.service_type,
                publish_config=body.config,
            )
        return PublishResponse.model_validate(service)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("", response_model=PublishListResponse)
def list_services():
    services = publisher.list_services()
    return PublishListResponse(
        services=[PublishResponse.model_validate(s) for s in services],
        total=len(services),
    )


@router.get("/{service_id}", response_model=PublishResponse)
def get_service(service_id: int):
    service = publisher.get_service(service_id)
    if not service:
        raise HTTPException(404, f"Service id={service_id} not found")
    return PublishResponse.model_validate(service)


@router.post("/{service_id}/stop")
async def stop_service(service_id: int):
    try:
        await publisher.stop_service(service_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{service_id}")
async def delete_service(service_id: int):
    try:
        await publisher.delete_service(service_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, str(e))
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/routers/publishing.py
git commit -m "feat: add publishing API routes"
```

---

### 任务 11：FastAPI 主入口

**文件：**
- 创建：`AIStudio/backend/main.py`

- [ ] **步骤 1：编写 main.py**

`AIStudio/backend/main.py`:
```python
"""AIStudio backend - FastAPI application."""

import os
import sys

# Ensure backend package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import init_db
from .routers import models_router, training_router, evaluation_router, publishing_router

app = FastAPI(
    title="AIStudio",
    description="AI Workflow Platform - Model Lifecycle Management",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models_router)
app.include_router(training_router)
app.include_router(evaluation_router)
app.include_router(publishing_router)


@app.on_event("startup")
def on_startup():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    os.makedirs(config.HF_CACHE_DIR, exist_ok=True)
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


def main():
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
```

- [ ] **步骤 2：启动后端并验证**

运行：`cd AIStudio/backend && python3 main.py`
预期：终端显示 Uvicorn running on http://127.0.0.1:8000

另一个终端测试：
```bash
curl http://127.0.0.1:8000/api/health
```
预期：`{"status":"ok"}`

测试模型 CRUD：
```bash
curl -X POST http://127.0.0.1:8000/api/models \
  -H "Content-Type: application/json" \
  -d '{"name":"test-model","source":"local","source_path":"/tmp/test","model_type":"llm","description":"test"}'
```
预期：201 with model data

```bash
curl http://127.0.0.1:8000/api/models
```
预期：`{"models":[...],"total":1}`

- [ ] **步骤 3：Commit**

```bash
git add AIStudio/backend/main.py
git commit -m "feat: add FastAPI main entry with startup and health endpoint"
```

---

### 任务 12：训练脚本

**文件：**
- 创建：`AIStudio/backend/scripts/__init__.py`
- 创建：`AIStudio/backend/scripts/train_lora.py`

- [ ] **步骤 1：创建 scripts 包**

`AIStudio/backend/scripts/__init__.py`:
```python
"""Executable scripts for training and evaluation subprocesses."""
```

- [ ] **步骤 2：编写 train_lora.py**

`AIStudio/backend/scripts/train_lora.py`:
```python
#!/usr/bin/env python3
"""
LoRA/QLoRA training script.

Invoked by training_runner.py as a subprocess.
Reads config JSON from argv[1], writes result.json to work_dir.

Usage: python3 train_lora.py <path/to/config.json>
"""

import json
import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: train_lora.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1])
    config = json.loads(config_path.read_text())

    work_dir = config_path.parent
    result_path = work_dir / "result.json"

    try:
        base_model_path = config["base_model"]
        method = config.get("method", "lora")
        output_dir = config["output_dir"]
        dataset_path = config.get("dataset_path", "")
        learning_rate = float(config.get("learning_rate", 2e-4))
        num_epochs = int(config.get("num_epochs", 3))
        batch_size = int(config.get("batch_size", 4))
        lora_r = int(config.get("lora_r", 8))
        lora_alpha = int(config.get("lora_alpha", 32))
        max_length = int(config.get("max_length", 512))

        print(f"[train_lora] Starting training...")
        print(f"  Base model: {base_model_path}")
        print(f"  Method: {method}")
        print(f"  Output: {output_dir}")
        print(f"  Dataset: {dataset_path}")

        # Import heavy dependencies inside the subprocess
        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
            Trainer,
            DataCollatorForSeq2Seq,
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from datasets import load_dataset

        print("[train_lora] Loading model...")
        kwargs = {"torch_dtype": torch.bfloat16, "device_map": "auto"}
        if method == "qlora":
            kwargs["quantization_config"] = {
                "load_in_4bit": True,
                "bnb_4bit_compute_dtype": torch.bfloat16,
            }

        model = AutoModelForCausalLM.from_pretrained(base_model_path, **kwargs)
        tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # LoRA config
        target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
        lora_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        # Load dataset
        if dataset_path:
            print(f"[train_lora] Loading dataset from {dataset_path}")
            dataset = load_dataset("json", data_files=dataset_path, split="train")

            def tokenize_fn(examples):
                texts = examples.get("text", examples.get("instruction", [""]))
                if isinstance(texts, str):
                    texts = [texts]
                model_inputs = tokenizer(
                    texts, truncation=True, max_length=max_length, padding=False
                )
                model_inputs["labels"] = model_inputs["input_ids"].copy()
                return model_inputs

            tokenized = dataset.map(tokenize_fn, remove_columns=dataset.column_names)
            data_collator = DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8)
        else:
            print("[train_lora] No dataset provided, using dummy data")
            # Create tiny dummy dataset
            dummy = tokenizer(
                ["Hello world"] * 10, truncation=True, max_length=max_length, padding=False
            )
            dummy["labels"] = dummy["input_ids"].copy()
            tokenized = dummy
            data_collator = None

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            bf16=torch.cuda.is_available(),
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=2,
            remove_unused_columns=False,
            report_to="none",
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )

        print("[train_lora] Starting training loop...")
        trainer.train()

        print(f"[train_lora] Saving model to {output_dir}")
        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)

        # Write result
        result = {
            "status": "completed",
            "output_path": output_dir,
            "metrics": {
                "train_loss": float(trainer.state.log_history[-1].get("loss", 0))
                if trainer.state.log_history else 0,
            },
        }
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[train_lora] Training completed. Results written to {result_path}")

    except Exception as e:
        print(f"[train_lora] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        result = {"status": "failed", "error": str(e)}
        result_path.write_text(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 3：Commit**

```bash
git add AIStudio/backend/scripts/__init__.py AIStudio/backend/scripts/train_lora.py
git commit -m "feat: add LoRA/QLoRA training script"
```

---

### 任务 13：评估脚本

**文件：**
- 创建：`AIStudio/backend/scripts/evaluate.py`

- [ ] **步骤 1：编写 evaluate.py**

`AIStudio/backend/scripts/evaluate.py`:
```python
#!/usr/bin/env python3
"""
Evaluation script.

Invoked by evaluator.py as a subprocess.
Reads config JSON from argv[1], writes result.json to work_dir.

Usage: python3 evaluate.py <path/to/config.json>
"""

import json
import math
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: evaluate.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1])
    config = json.loads(config_path.read_text())

    work_dir = config_path.parent
    result_path = work_dir / "result.json"

    try:
        model_path = config["model_path"]
        model_type = config.get("model_type", "llm")
        eval_type = config.get("eval_type", "perplexity")
        dataset = config.get("dataset", "")

        print(f"[evaluate] Starting evaluation...")
        print(f"  Model: {model_path}")
        print(f"  Type: {eval_type}")
        print(f"  Dataset: {dataset}")

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print("[evaluate] Loading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path, torch_dtype=torch.bfloat16, device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model.eval()

        metrics = {}

        if eval_type == "perplexity":
            # Compute perplexity on dataset or a sample
            if dataset:
                from datasets import load_dataset
                data = load_dataset("json", data_files=dataset, split="train")
                texts = data.get("text", data.get("instruction", []))
            else:
                # Use a small default sample
                texts = [
                    "The quick brown fox jumps over the lazy dog.",
                    "Machine learning is a subset of artificial intelligence.",
                    "Transformers have revolutionized natural language processing.",
                ]

            encodings = tokenizer(
                texts, truncation=True, padding=True, max_length=512, return_tensors="pt"
            )
            input_ids = encodings.input_ids
            attn_mask = encodings.attention_mask

            max_length = 512
            stride = 256
            nlls = []

            with torch.no_grad():
                for i in range(0, input_ids.size(1), stride):
                    begin_loc = max(i, 0)
                    end_loc = min(i + max_length, input_ids.size(1))
                    if end_loc - begin_loc < 10:
                        break
                    trg_len = end_loc - begin_loc
                    input_ids_chunk = input_ids[:, begin_loc:end_loc]
                    attn_chunk = attn_mask[:, begin_loc:end_loc] if attn_mask is not None else None

                    outputs = model(input_ids_chunk, attention_mask=attn_chunk, labels=input_ids_chunk)
                    loss = outputs.loss
                    nlls.append(loss.item() * trg_len)

            if nlls:
                ppl = math.exp(sum(nlls) / sum(
                    min(max_length, input_ids.size(1) - i) if (i + max_length) <= input_ids.size(1)
                    else input_ids.size(1) - i
                    for i in range(0, input_ids.size(1), stride)
                    if (input_ids.size(1) - i) >= 10
                ))
                metrics["perplexity"] = round(ppl, 4)
                print(f"[evaluate] Perplexity: {ppl:.4f}")

        elif eval_type == "benchmark":
            # Simple accuracy benchmark
            if dataset:
                from datasets import load_dataset
                data = load_dataset("json", data_files=dataset, split="train")
                correct = 0
                total = 0
                for item in data:
                    prompt = item.get("question", item.get("text", ""))
                    answer = item.get("answer", item.get("label", ""))
                    if not prompt or not answer:
                        continue
                    inputs = tokenizer(prompt, return_tensors="pt")
                    with torch.no_grad():
                        outputs = model.generate(**inputs, max_new_tokens=20)
                    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    if answer in generated:
                        correct += 1
                    total += 1
                accuracy = correct / total if total > 0 else 0
                metrics["accuracy"] = round(accuracy, 4)
                metrics["total_samples"] = total
                print(f"[evaluate] Accuracy: {accuracy:.4f} ({correct}/{total})")
            else:
                metrics["note"] = "No dataset provided for benchmark"

        elif eval_type == "custom":
            metrics["note"] = "Custom evaluation not implemented - extend evaluate.py"

        result = {
            "status": "completed",
            "metrics": metrics,
        }
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[evaluate] Completed. Results: {json.dumps(metrics)}")

    except Exception as e:
        print(f"[evaluate] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        result = {"status": "failed", "error": str(e)}
        result_path.write_text(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/scripts/evaluate.py
git commit -m "feat: add evaluation script (perplexity, benchmark)"
```

---

### 任务 14：API 发布推理服务脚本

**文件：**
- 创建：`AIStudio/backend/scripts/api_server.py`

- [ ] **步骤 1：编写 api_server.py**

`AIStudio/backend/scripts/api_server.py`:
```python
#!/usr/bin/env python3
"""
Inference server for published models.

Invoked by publisher.py as a subprocess.
Provides OpenAI-compatible chat completion and embedding endpoints.

Usage: python3 api_server.py --model_path <path> --model_type <llm|embedding> --host <host> --port <port>
"""

import argparse
import json
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AIStudio Inference Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_model = None
_tokenizer = None
_model_type = None


class ChatRequest(BaseModel):
    model: str = ""
    messages: list[dict]
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9


class EmbeddingRequest(BaseModel):
    model: str = ""
    input: list[str]


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    if _model_type != "llm":
        raise HTTPException(400, "Model is not an LLM")

    # Format prompt from messages
    prompt_parts = []
    for msg in req.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
    prompt_parts.append("Assistant: ")
    prompt = "\n".join(prompt_parts)

    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    outputs = _model.generate(
        **inputs,
        max_new_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        do_sample=req.temperature > 0,
        pad_token_id=_tokenizer.pad_token_id,
    )
    response_text = _tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": inputs.input_ids.shape[1],
            "completion_tokens": outputs.shape[1] - inputs.input_ids.shape[1],
            "total_tokens": outputs.shape[1],
        },
    }


@app.post("/v1/embeddings")
async def embeddings(req: EmbeddingRequest):
    if _model_type not in ("embedding", "llm"):
        raise HTTPException(400, f"Model type '{_model_type}' does not support embeddings")

    import torch
    all_embeddings = []
    for text in req.input:
        inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(_model.device)
        with torch.no_grad():
            outputs = _model(**inputs, output_hidden_states=True)
            # Use mean pooling of last hidden state
            last_hidden = outputs.hidden_states[-1] if hasattr(outputs, "hidden_states") else outputs.last_hidden_state
            mask = inputs.attention_mask.unsqueeze(-1).float()
            pooled = (last_hidden * mask).sum(dim=1) / mask.sum(dim=1)
            embedding = pooled[0].cpu().tolist()
            all_embeddings.append(embedding)

    return {
        "model": req.model,
        "data": [
            {"object": "embedding", "index": i, "embedding": emb}
            for i, emb in enumerate(all_embeddings)
        ],
        "usage": {"total_tokens": 0},
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": _model is not None,
        "model_type": _model_type,
    }


def main():
    parser = argparse.ArgumentParser(description="AIStudio Inference Server")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--model_type", default="llm", choices=["llm", "embedding"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8300)
    parser.add_argument("--service_id", type=int, default=0)
    args = parser.parse_args()

    global _model, _tokenizer, _model_type
    _model_type = args.model_type

    print(f"[api_server] Loading model from {args.model_path}")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    _model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        output_hidden_states=True,
    )
    _tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    _model.eval()
    print(f"[api_server] Model loaded. Starting server on {args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/backend/scripts/api_server.py
git commit -m "feat: add inference server script for model publishing"
```

---

### 任务 15：验证后端启动

**描述：** 确认后端可以通过 `pip install -r requirements.txt` 安装依赖并启动。

- [ ] **步骤 1：安装依赖并启动测试**

```bash
cd AIStudio/backend
pip install -r requirements.txt
python3 -c "from main import app; print('App loaded OK')"
```

预期：`App loaded OK`

- [ ] **步骤 2：启动并测试全流程**

```bash
cd AIStudio/backend
python3 main.py &
sleep 3

# Health
curl http://127.0.0.1:8000/api/health

# Create model
curl -s -X POST http://127.0.0.1:8000/api/models \
  -H "Content-Type: application/json" \
  -d '{"name":"test-model","source":"local","source_path":"Qwen/Qwen2.5-0.5B","model_type":"llm"}' | python3 -m json.tool

# List models
curl -s http://127.0.0.1:8000/api/models | python3 -m json.tool

kill %1 2>/dev/null
```

预期：所有请求返回 2xx

- [ ] **步骤 3：Commit 最终调整**

```bash
git add -A
git commit -m "chore: finalize backend setup"
```
