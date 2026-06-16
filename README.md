# AIStudio — AI 工作流平台

> 本地运行的 AI 模型生命周期管理平台，支持 LLM 和 Embedding 模型的导入、微调（LoRA/QLoRA）、评估和发布。

## 目录

- [功能概览](#功能概览)
- [架构](#架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
  - [前置要求](#前置要求)
  - [后端启动](#后端启动)
  - [前端启动](#前端启动)
- [使用指南](#使用指南)
  - [模型管理](#1-模型管理)
  - [模型训练](#2-模型训练)
  - [模型评估](#3-模型评估)
  - [模型发布](#4-模型发布)
- [配置说明](#配置说明)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [开发说明](#开发说明)

---

## 功能概览

| 模块 | 功能 | 说明 |
|------|------|------|
| **模型管理** | 导入、列表、详情、删除 | 支持从 HuggingFace 下载或本地路径导入 |
| **模型训练** | LoRA / QLoRA 微调 | 通过子进程独立运行训练脚本，支持超参配置 |
| **模型评估** | 困惑度 / 基准测试 | 子进程运行评估，实时查看日志和指标 |
| **模型发布** | API 服务 / 文件导出 | 发布为 OpenAI 兼容的推理端点，或导出合并权重 |

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    Vue 3 + Naive UI                      │
│  (localhost:5173)                                        │
│  模型管理 | 训练 | 评估 | 发布                           │
└──────────────┬──────────────────────────────────────────┘
               │ HTTP /api/* (Vite proxy)
               ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (Python)                      │
│  (127.0.0.1:8000)                                       │
│  routers/ → services/ → models/ (ORM)                   │
└──────────────┬──────────────────────────────────────────┘
               │ subprocess
               ▼
┌─────────────────────────────────────────────────────────┐
│  scripts/                                                │
│  train_lora.py  │  evaluate.py  │  api_server.py         │
└─────────────────────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Naive UI |
| 后端 | FastAPI + SQLAlchemy 2.0 + SQLite |
| AI 框架 | transformers + peft + datasets + huggingface-hub |
| 运行环境 | Python 3.10+, Node.js 18+ |

## 快速开始

### 前置要求

```bash
python3 --version   # ≥ 3.10
node --version      # ≥ 18
npm --version       # ≥ 9
```

### 后端启动

```bash
# 1. 安装依赖
cd AIStudio/backend
pip install -r requirements.txt

# 2. 启动后端（开发模式，自动重载）
cd ..  # 回到 AIStudio/ 目录
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload --reload-exclude 'data/*'
```

验证后端运行：
```bash
curl http://127.0.0.1:8000/api/health
# 输出: {"status":"ok"}
```

### 前端启动

```bash
# 1. 安装依赖
cd AIStudio/frontend
npm install

# 2. 启动开发服务器
npm run dev
```

打开浏览器访问 **http://localhost:5173**

前端通过 Vite 代理将 `/api` 请求转发到后端（`http://127.0.0.1:8000`）。

### 启动演示

两个终端并行运行：
```bash
# 终端 1 - 后端
cd AIStudio && python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload --reload-exclude 'data/*'

# 终端 2 - 前端
cd AIStudio/frontend && npm run dev
```

## 使用指南

### 1. 模型管理

**导入模型：**
1. 左侧导航 → **模型管理**
2. 点击 **导入模型**
3. 填写模型名称，选择来源：
   - **HuggingFace**：填写模型 ID（如 `Qwen/Qwen2.5-7B`）
   - **本地路径**：填写模型文件所在目录的绝对路径
4. 选择模型类型（LLM / Embedding）
5. 点击确认，模型即注册到平台

**操作：**
- 点击 **详情** 查看模型完整信息和关联任务
- HuggingFace 来源的模型可点击 **下载** 将权重文件下载到本地
- 点击 **删除** 移除模型及本地文件（有运行中的发布服务时会阻止删除）

### 2. 模型训练

**发起训练：**
1. 左侧导航 → **模型训练**
2. 点击 **新建训练**
3. 选择模型（仅显示 `ready` 状态的 LLM 模型）
4. 配置训练参数：
   - **训练方法**：LoRA 或 QLoRA（4-bit 量化）
   - **数据集路径**：JSONL 格式的本地文件路径（可选，不提供则使用 dummy 数据验证流程）
   - 学习率、训练轮数、Batch Size、最大长度
   - LoRA 参数：rank（r）和 alpha
5. 点击 **开始训练**，后台自动启动子进程运行

**查看进度：**
- 列表页实时显示任务状态
- 点击任务详情查看运行日志（运行中每 3 秒自动刷新）
- 运行中的任务可以 **取消**

### 3. 模型评估

**发起评估：**
1. 左侧导航 → **模型评估**
2. 点击 **新建评估**
3. 选择模型，选择评估类型：
   - **Perplexity（困惑度）**：计算模型在验证集上的困惑度
   - **Benchmark（基准测试）**：运行问答应答测试计算准确率
   - **Custom（自定义）**：预留扩展点
4. 可选数据集路径，点击 **开始评估**

**查看结果：**
- 评估完成后自动显示指标（如 `perplexity` 值、`accuracy` 等）
- 支持查看评估过程日志

### 4. 模型发布

**API 服务发布：**
1. 左侧导航 → **模型发布**
2. 点击 **新建发布**
3. 选择模型，发布类型选 **API 服务**
4. 配置端口号和 Max Tokens
5. 服务启动后自动生成 `http://127.0.0.1:{port}` 端点
6. 支持 OpenAI 兼容格式：
   - `POST /v1/chat/completions`（LLM 模型）
   - `POST /v1/embeddings`（Embedding 模型）
7. 可随时 **停止** 或 **删除** 服务

**文件导出：**
1. 新建发布时类型选择 **导出文件**
2. 填写目标导出路径
3. 系统将模型文件复制（如需 PEFT 合并则记录合并信息）到目标路径

## 配置说明

通过环境变量配置后端：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AISTUDIO_HOST` | `127.0.0.1` | 后端监听地址 |
| `AISTUDIO_PORT` | `8000` | 后端监听端口 |
| `AISTUDIO_DATA_DIR` | `AIStudio/data` | 数据目录（数据库、日志） |
| `AISTUDIO_MODELS_DIR` | `AIStudio/data/models` | 模型文件存储目录 |
| `AISTUDIO_DB_PATH` | `AIStudio/data/aistudio.db` | SQLite 数据库文件路径 |
| `HF_TOKEN` | 空 | HuggingFace 认证令牌（私有仓库需要） |

示例：
```bash
AISTUDIO_PORT=9000 HF_TOKEN=hf_xxx python3 -m uvicorn backend.main:app --port 9000
```

## 项目结构

```
AIStudio/
├── backend/                     # Python 后端
│   ├── main.py                  # FastAPI 应用入口
│   ├── config.py                # 配置
│   ├── database.py              # SQLAlchemy 引擎
│   ├── models/                  # ORM 模型
│   ├── schemas/                 # Pydantic 数据模型
│   ├── routers/                 # API 路由
│   ├── services/                # 业务逻辑
│   ├── scripts/                 # 独立可执行脚本
│   │   ├── train_lora.py        # LoRA 微调
│   │   ├── evaluate.py          # 模型评估
│   │   └── api_server.py        # 推理服务
│   └── requirements.txt
├── frontend/                    # Vue3 前端
│   ├── src/
│   │   ├── App.vue              # 主布局
│   │   ├── router/              # 路由
│   │   ├── views/               # 页面组件
│   │   ├── components/          # 通用组件
│   │   ├── api/                 # API 客户端
│   │   └── types/               # TypeScript 类型
│   └── package.json
├── data/                        # 运行时数据（自动创建）
│   ├── aistudio.db              # SQLite 数据库
│   └── models/                  # 下载的模型文件
├── docs/
│   ├── specs/                   # 设计文档
│   └── plans/                   # 实现计划
├── test-integration.sh          # 前后端集成测试脚本
└── README.md
```

## 常见问题

**Q: 启动后端报错 "Address already in use"**

```bash
# 查找并释放端口
lsof -ti:8000 | xargs kill -9
```

**Q: 前端页面空白或无法加载**

确认后端已启动且端口正确，检查浏览器控制台是否有 CORS 错误：
- 后端默认允许 `http://127.0.0.1:5173` 和 `http://localhost:5173`
- 前端 Vite 代理将 `/api` 请求转发到 `http://127.0.0.1:8000`

**Q: 前端页面有导航栏，但表格/按钮不显示**

打开浏览器开发者工具（F12 → Console），如果看到关于 `useMessage()` 或 `injection not found` 的错误，说明缺少 Naive UI 的 Provider 包装。确保 `App.vue` 的模板最外层包含 `<n-message-provider>`（以及 `<n-dialog-provider>`、`<n-notification-provider>`）。

**Q: 模型下载失败**

- 检查网络连接
- 公有模型不需要认证，私有仓库需要设置 `HF_TOKEN` 环境变量
- 确认 HuggingFace 模型 ID 正确

**Q: 训练任务启动后立即失败**

- 训练脚本从数据库读取模型路径，确保 `source_path` 指向有效的模型目录
- 查看训练详情页的日志，了解具体错误信息
- 缺少依赖时安装：`pip install torch transformers peft datasets bitsandbytes`

**Q: 数据库重置**

```bash
rm -f AIStudio/data/aistudio.db
# 重启后端后会自动创建新的数据库
```

## 开发说明

### API 文档

后端启动后访问 http://127.0.0.1:8000/docs 查看 Swagger 交互式 API 文档。

### 开发模式

- 后端 `--reload` 模式下代码变更自动重载
- 前端 Vite 开发服务器支持 HMR（热模块替换）

### 运行测试

```bash
# 后端导入验证
cd AIStudio && python3 -c "from backend.main import app; print('Backend OK')"

# 前端类型检查
cd AIStudio/frontend && npx vue-tsc --noEmit

# 前端构建
cd AIStudio/frontend && npm run build

# 前后端集成测试（确保前后端都在运行）
bash AIStudio/test-integration.sh
```

集成测试脚本包含 8 项检测：后端健康检查、前端服务检查、Vite 代理验证、模型 CRUD、训练/评估/发布 API 测试，以及测试数据清理。

---

> 项目代码和文档全部放在 `AIStudio/` 目录下。设计文档见 `docs/specs/`，实现计划见 `docs/plans/`。
