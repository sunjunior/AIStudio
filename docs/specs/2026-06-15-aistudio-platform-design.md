# AIStudio — AI 工作流平台设计文档

> AI 模型生命周期管理平台（本地版），支持 LLM 和 Embedding 模型的导入、微调、评估和发布。

## 1. 概述

### 目标

构建一个本地运行的 AI 模型生命周期管理平台，涵盖从模型导入到发布的全流程：

- **模型管理** — 从 HuggingFace 导入、本地导入、删除模型
- **模型训练** — LoRA/QLoRA 微调，任务队列管理
- **模型评估** — 困惑度评估、自定义评估流程
- **模型发布** — 发布为本地 API 服务或导出模型文件

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript + Vite | SPA 应用 |
| UI 库 | Naive UI | 组件库 |
| 路由 | Vue Router 4 | 前端路由 |
| HTTP 客户端 | Axios | API 通信 |
| 后端框架 | FastAPI (Python 3.10+) | REST API |
| 数据库 | SQLite (via SQLAlchemy + aiosqlite) | 元数据存储 |
| 模型生态 | transformers + peft + trl + bitsandbytes | 模型加载与训练 |
| 进程管理 | asyncio.subprocess | 训练/评估子进程 |

### 约束

- 所有数据存储在本地单机，无外部服务依赖
- 训练和评估在独立子进程中执行，不阻塞后端
- 模型文件存储在本地文件系统

## 2. 目录结构

```
AIStudio/
├── backend/
│   ├── main.py                         # FastAPI 应用入口
│   ├── config.py                       # 全局配置（路径、默认参数）
│   ├── database.py                     # SQLAlchemy 引擎 + 会话
│   ├── models/                         # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── model_registry.py           # 模型注册表
│   │   ├── training_task.py            # 训练任务
│   │   ├── evaluation_record.py        # 评估记录
│   │   └── published_service.py        # 发布服务记录
│   ├── schemas/                        # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── model.py
│   │   ├── training.py
│   │   ├── evaluation.py
│   │   └── publishing.py
│   ├── routers/                        # API 路由
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── training.py
│   │   ├── evaluation.py
│   │   └── publishing.py
│   ├── services/                       # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── model_manager.py
│   │   ├── training_runner.py
│   │   ├── evaluator.py
│   │   └── publisher.py
│   ├── scripts/                        # 独立可执行脚本
│   │   ├── train_lora.py               # LoRA 微调脚本
│   │   └── evaluate.py                 # 评估脚本
│   ├── requirements.txt                # Python 依赖
│   └── .env.example                    # 环境变量模板
│
├── frontend/
│   ├── src/
│   │   ├── main.ts                     # Vue 入口
│   │   ├── App.vue                     # 根组件
│   │   ├── router/
│   │   │   └── index.ts                # 路由定义
│   │   ├── api/
│   │   │   ├── client.ts               # Axios 实例
│   │   │   ├── models.ts               # 模型相关 API
│   │   │   ├── training.ts             # 训练相关 API
│   │   │   ├── evaluation.ts           # 评估相关 API
│   │   │   └── publishing.ts           # 发布相关 API
│   │   ├── views/
│   │   │   ├── ModelsView.vue          # 模型列表
│   │   │   ├── ModelDetailView.vue     # 模型详情
│   │   │   ├── TrainingView.vue        # 训练任务列表
│   │   │   ├── TrainingDetailView.vue  # 训练详情
│   │   │   ├── EvaluationView.vue      # 评估记录列表
│   │   │   ├── EvaluationDetailView.vue# 评估详情
│   │   │   └── PublishView.vue         # 发布管理
│   │   ├── components/
│   │   │   ├── ModelSelector.vue       # 模型选择器
│   │   │   ├── TaskStatusBadge.vue     # 状态标签
│   │   │   └── LogViewer.vue           # 日志查看器
│   │   └── types/
│   │       └── index.ts               # TypeScript 类型定义
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── data/                              # 运行时数据目录
│   ├── aistudio.db                    # SQLite 数据库
│   └── models/                        # 模型文件存储
│
├── docs/
│   └── specs/
│       └── 2026-06-15-aistudio-platform-design.md  # 本文档
│
└── README.md
```

## 3. 数据库设计

使用 SQLAlchemy ORM + SQLite。所有表存储在 `data/aistudio.db`。

### 3.1 models — 模型注册表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | 自增 ID |
| name | String(255) | UNIQUE, NOT NULL | 模型名称，如 `Qwen2.5-7B` |
| source | String(50) | NOT NULL | `huggingface` / `local` / `uploaded` |
| source_path | String(512) | | HF 模型 ID（如 `Qwen/Qwen2.5-7B`）或本地路径 |
| model_type | String(50) | NOT NULL | `llm` / `embedding` / `peft_checkpoint` |
| base_model_id | Integer | FK → models.id | 如果是 LoRA 适配器，指向基座模型 |
| status | String(50) | NOT NULL, DEFAULT `ready` | `downloading` / `ready` / `error` |
| local_path | String(512) | | 本地存储路径 |
| description | Text | | 用户备注 |
| created_at | DateTime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTime | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

### 3.2 training_tasks — 训练任务

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | 自增 ID |
| model_id | Integer | FK → models.id, NOT NULL | 被训练的模型 |
| method | String(50) | NOT NULL | `lora` / `qlora` |
| config | Text | NOT NULL | JSON 超参 |
| status | String(50) | NOT NULL, DEFAULT `pending` | `pending` / `running` / `completed` / `failed` / `cancelled` |
| pid | Integer | | 子进程 PID（运行时） |
| log_path | String(512) | | 日志文件路径 |
| output_model_id | Integer | FK → models.id | 训练产物（新的 PEFT 适配器模型） |
| error_message | Text | | 失败时的错误信息 |
| started_at | DateTime | | 开始时间 |
| finished_at | DateTime | | 完成时间 |
| created_at | DateTime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3.3 evaluation_records — 评估记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | 自增 ID |
| model_id | Integer | FK → models.id, NOT NULL | 被评估的模型 |
| eval_type | String(50) | NOT NULL | `perplexity` / `benchmark` / `custom` |
| dataset | String(512) | | 评估数据集名称或路径 |
| metrics | Text | | JSON 评估结果 |
| status | String(50) | NOT NULL, DEFAULT `pending` | `pending` / `running` / `completed` / `failed` |
| log_path | String(512) | | 日志路径 |
| error_message | Text | | 失败时的错误信息 |
| created_at | DateTime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3.4 published_services — 发布的服务

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, autoincrement | 自增 ID |
| model_id | Integer | FK → models.id, NOT NULL | 发布的模型 |
| service_type | String(50) | NOT NULL | `api` / `export` |
| endpoint | String(512) | | API 服务地址 |
| export_path | String(512) | | 导出路径 |
| config | Text | | JSON 服务参数 |
| status | String(50) | NOT NULL, DEFAULT `stopped` | `running` / `stopped` / `failed` |
| pid | Integer | | API 服务子进程 PID |
| error_message | Text | | 失败时的错误信息 |
| created_at | DateTime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| stopped_at | DateTime | | 停止时间 |

### 3.5 ER 关系

```
models 1──N training_tasks     (model_id)
models 1──N training_tasks     (output_model_id, 训练产物)
models 1──N evaluation_records (model_id)
models 1──N published_services (model_id)
models 1──N models             (base_model_id, 自引用, LoRA→基座)
```

## 4. API 路由设计

所有路由前缀 `/api`。后端在 `http://127.0.0.1:8000` 运行。

### 4.1 模型管理 — `/api/models`

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| GET | `/api/models` | query: `type`, `status` | `Model[]` | 模型列表 |
| GET | `/api/models/:id` | | `Model` | 模型详情 |
| POST | `/api/models` | `{name, source, source_path, model_type, description}` | `Model` | 注册模型 |
| DELETE | `/api/models/:id` | | `{success}` | 删除模型及文件 |
| POST | `/api/models/:id/download` | | `{task_id}` | 启动下载（异步） |
| GET | `/api/models/:id/download/status` | | `{status, progress}` | 下载进度 |

### 4.2 训练管理 — `/api/training`

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| POST | `/api/training` | `{model_id, method, config}` | `Task` | 创建训练任务 |
| GET | `/api/training` | query: `status` | `Task[]` | 任务列表 |
| GET | `/api/training/:id` | | `Task` | 任务详情 |
| POST | `/api/training/:id/cancel` | | `{success}` | 取消任务 |
| GET | `/api/training/:id/logs` | | `{logs: string}` | 获取日志 |

### 4.3 评估管理 — `/api/evaluation`

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| POST | `/api/evaluation` | `{model_id, eval_type, dataset}` | `EvalRecord` | 创建评估 |
| GET | `/api/evaluation` | query: `status` | `EvalRecord[]` | 评估列表 |
| GET | `/api/evaluation/:id` | | `EvalRecord` | 评估详情 |
| DELETE | `/api/evaluation/:id` | | `{success}` | 删除记录 |
| GET | `/api/evaluation/:id/logs` | | `{logs: string}` | 获取日志 |

### 4.4 发布管理 — `/api/publishing`

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| POST | `/api/publishing` | `{model_id, service_type, config}` | `PublishedService` | 创建发布 |
| GET | `/api/publishing` | | `PublishedService[]` | 发布列表 |
| POST | `/api/publishing/:id/stop` | | `{success}` | 停止服务 |
| DELETE | `/api/publishing/:id` | | `{success}` | 移除发布 |

## 5. 后端设计

### 5.1 服务层结构

**`model_manager.py`** — 模型文件管理
- `register_model()` — 向数据库注册模型条目
- `delete_model()` — 删除数据库记录 + 清理本地文件
- `download_model()` — 调用 `huggingface_hub` 下载模型文件到 `data/models/<name>/`
- `get_model_path()` — 返回模型本地路径
- `list_models()` — 按 type/status 过滤列表

**`training_runner.py`** — 训练任务管理
- `create_task()` — 插入任务记录，返回 task_id
- `start_task()` — 启动子进程运行 `scripts/train_lora.py`
- `cancel_task()` — 发送 SIGTERM → SIGKILL 超时策略
- `update_task_status()` — 子进程结束后更新状态
- `get_task_logs()` — 读取日志文件尾部

**`evaluator.py`** — 评估管理
- `create_evaluation()` — 插入评估记录
- `run_evaluation()` — 启动子进程运行 `scripts/evaluate.py`
- `get_results()` — 解析 result.json 返回评估指标

**`publisher.py`** — 发布管理
- `publish_api()` — 启动 vLLM / transformers 推理服务子进程
- `publish_export()` — 合并 LoRA 权重 → 导出到目标目录
- `stop_service()` — 停止 API 服务进程

### 5.2 子进程管理协议

训练和评估通过独立 Python 子进程执行，遵循统一的文件协议：

```
后端 (training_runner.py)
    │  写入 config.json (含 task_id 等参数)
    ▼
subprocess python3 scripts/train_lora.py
    │  读取 config.json
    │  执行训练
    │  写入日志到 stdout/stderr（后端捕获写入文件）
    │  训练完成 → 写入 result.json
    ▼
后端 检测到进程退出
    │  读取 result.json
    │  更新 training_tasks 状态
    │  创建 output_model 记录
```

**result.json 格式：**
```json
{
  "status": "completed",
  "output_path": "/path/to/adapter",
  "metrics": {"train_loss": 0.32, "eval_loss": 0.41},
  "error": null
}
```

### 5.3 配置文件 (`config.py`)

```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
MODELS_DIR = os.path.join(DATA_DIR, "models")
DB_PATH = os.path.join(DATA_DIR, "aistudio.db")
HF_CACHE_DIR = os.path.join(DATA_DIR, "hf_cache")
TRAINING_SCRIPT = os.path.join(BASE_DIR, "scripts", "train_lora.py")
EVAL_SCRIPT = os.path.join(BASE_DIR, "scripts", "evaluate.py")
API_HOST = "127.0.0.1"
API_PORT = 8000
```

## 6. 前端设计

### 6.1 路由

| 路径 | 视图 | 说明 |
|------|------|------|
| `/` | 重定向 → `/models` | 首页 |
| `/models` | ModelsView | 模型列表（数据表格、导入按钮） |
| `/models/:id` | ModelDetailView | 模型详情 + 关联任务列表 |
| `/training` | TrainingView | 训练任务列表（新建任务按钮） |
| `/training/:id` | TrainingDetailView | 任务详情 + 日志 + 进度 |
| `/evaluation` | EvaluationView | 评估记录列表 |
| `/evaluation/:id` | EvaluationDetailView | 评估结果详情 |
| `/publishing` | PublishView | 发布服务列表（新建发布） |

### 6.2 页面功能说明

**ModelsView（模型列表）：**
- NDataTable 展示所有模型（名称、类型、状态、来源、时间）
- 顶部搜索/过滤（按类型、状态）
- "导入模型"按钮 → NForm 对话框（填名称、HF ID 或本地路径）
- 每行操作：详情、删除、发起训练、发起评估
- 下载中状态显示 NProgress

**ModelDetailView（模型详情）：**
- 模型基本信息（NCard）
- 关联的训练任务列表
- 关联的评估记录列表
- 关联的发布服务列表
- 操作：训练、评估、发布、删除

**TrainingView（训练列表）：**
- NDataTable 展示训练任务（模型、方法、状态、时间）
- "新建训练"按钮 → 选择模型 + 配置超参表单
- 运行中的任务可取消

**TrainingDetailView（训练详情）：**
- 任务状态 + 配置信息
- LogViewer 组件实时展示日志
- 完成后显示产出模型

**PublishView（发布管理）：**
- 已发布服务列表
- "新建发布" → 选择模型 + 选择类型（API/导出）+ 配置参数
- API 服务可启动/停止
- 导出可查看导出路径

### 6.3 核心组件

**ModelSelector.vue：**
- Props: `modelType` (llm/embedding), `status` (ready only)
- 从 `/api/models` 获取列表，支持下筛选
- Emit: `select(model)`

**TaskStatusBadge.vue：**
- Props: `status`
- 渲染彩色 NTag（pending=默认、running=info、completed=success、failed=error、cancelled=warning）

**LogViewer.vue：**
- Props: `logPath`, `taskId`
- 轮询 `/api/training/:id/logs` 获取增量日志
- 自动滚动到底部，支持暂停自动滚动

### 6.4 TypeScript 类型 (`types/index.ts`)

```typescript
interface Model {
  id: number
  name: string
  source: 'huggingface' | 'local' | 'uploaded'
  source_path: string
  model_type: 'llm' | 'embedding' | 'peft_checkpoint'
  base_model_id: number | null
  status: 'downloading' | 'ready' | 'error'
  local_path: string
  description: string
  created_at: string
  updated_at: string
}

interface TrainingTask {
  id: number
  model_id: number
  method: 'lora' | 'qlora'
  config: Record<string, any>
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  log_path: string
  output_model_id: number | null
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

interface EvaluationRecord {
  id: number
  model_id: number
  eval_type: 'perplexity' | 'benchmark' | 'custom'
  dataset: string
  metrics: Record<string, any> | null
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
}

interface PublishedService {
  id: number
  model_id: number
  service_type: 'api' | 'export'
  endpoint: string | null
  export_path: string | null
  config: Record<string, any>
  status: 'running' | 'stopped' | 'failed'
  created_at: string
}
```

## 7. 训练脚本设计 (`scripts/train_lora.py`)

独立可执行脚本，通过标准文件协议与后端通信。

```python
"""
LoRA/QLoRA training script.
Invoked by training_runner.py as a subprocess.

Reads:  <work_dir>/config.json
Writes: <work_dir>/result.json
Logs:   stdout/stderr (captured by parent process)
"""
```

**功能：**
1. 读取 config.json
2. 使用 `transformers.AutoModelForCausalLM` + `PeftModel` 加载基座模型
3. 根据 method 配置 LoRA（`peft.LoraConfig`）或 QLoRA（+ `bitsandbytes`）
4. 加载数据集（JSONL 格式，`<work_dir>/dataset/`）
5. 使用 `transformers.Trainer` 或 `trl.SFTTrainer` 执行训练
6. 保存适配器权重到 config.output_dir
7. 写入 result.json

**评估脚本 (`scripts/evaluate.py`)：** 类似结构，支持 perplexity 计算和 benchmark 运行。

## 8. 发布机制

### 8.1 API 发布

- 启动一个独立的推理服务子进程，使用 `transformers` 加载模型权重提供 OpenAI 兼容接口
- 接口格式: `POST /v1/chat/completions`（LLM）和 `POST /v1/embeddings`（Embedding 模型）
- 子进程基于 FastAPI + `transformers`，启动时读取端口、模型路径等参数
- 通过配置端口启动，支持 `max_tokens`、`temperature`、`quantization` 等参数
- 后端记录子进程 PID，用于停止服务

### 8.2 导出发布

- 如果是 LoRA 适配器：使用 `peft` 合并权重到基座模型
- 可选量化导出（bitsandbytes）
- 导出到用户指定目录

## 9. 错误处理

| 场景 | 行为 |
|------|------|
| 模型导入时 HF ID 无效 | 返回 400，提示 "HuggingFace 模型不存在或无权访问" |
| 下载过程中断 | 标记为 error，清理不完整文件 |
| 训练 OOM | 子进程被 SIGKILL → 标记 failed，日志中 grep 最后 50 行返回前端 |
| 训练取消 | SIGTERM → 等 10s → SIGKILL，标记 cancelled |
| 端口冲突 | 发布 API 时检测端口占用，返回具体冲突信息 |
| 删除已发布服务的模型 | 返回 409，提示先停止关联的发布服务 |
| 数据集格式错误 | 评估脚本启动时预校验，失败快速返回 |

## 10. 启动与运行

```bash
# 后端
cd AIStudio/backend
pip install -r requirements.txt
python main.py
# → FastAPI running on http://127.0.0.1:8000

# 前端（另一个终端）
cd AIStudio/frontend
npm install
npm run dev
# → Vue dev server on http://127.0.0.1:5173 (proxied to :8000)
```

前端 dev server 通过 `vite.config.ts` 代理 `/api` 请求到后端：
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
})
```

## 11. 实现排期建议

| 阶段 | 内容 | 依赖 |
|------|------|------|
| 阶段 1 | 后端骨架（数据库 + 配置 + 基础路由） | 无 |
| 阶段 2 | 模型管理（CRUD + HF 导入/下载） | 阶段 1 |
| 阶段 3 | 训练系统（training_runner + train_lora 脚本） | 阶段 2 |
| 阶段 4 | 评估系统（evaluator + evaluate 脚本） | 阶段 2 |
| 阶段 5 | 发布系统（API 发布 + 导出） | 阶段 2 |
| 阶段 6 | 前端（所有视图 + 组件） | 阶段 1-5 |
| 阶段 7 | 集成测试 + 完善错误处理 | 全部 |

## 12. 未纳入范围（YAGNI）

以下功能明确不包含在此次实现中，未来如需可按需添加：

- 多用户认证与权限管理
- 可视化工作流编排（DAG 编辑器）
- 数据集管理（仅接受路径引用）
- GPU 资源池与调度
- WebSocket 实时日志（使用轮询替代）
- 容器化（Docker）
- 训练指标图表展示（仅展示数值）
