# AIStudio 前端实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现 AIStudio 的前端界面——Vue3 + TypeScript + Naive UI，覆盖模型管理、训练、评估和发布四个功能模块。

**架构：** SPA 应用，左侧固定导航栏 + 右侧内容区，通过 Axios 调用后端 REST API（/api/models, /api/training, /api/evaluation, /api/publishing）。

**技术栈：** Vue 3.4+, TypeScript, Vite 5, Vue Router 4, Naive UI 2.40+, Axios, @vicons/ionicons5

---

## 文件清单

| # | 文件 | 职责 |
|---|------|------|
| 1 | `frontend/package.json` | 项目依赖 |
| 2 | `frontend/vite.config.ts` | Vite 配置（含 API 代理） |
| 3 | `frontend/tsconfig.json` | TypeScript 配置 |
| 4 | `frontend/index.html` | HTML 入口 |
| 5 | `frontend/src/main.ts` | Vue 应用入口 |
| 6 | `frontend/src/App.vue` | 根组件（导航布局） |
| 7 | `frontend/src/router/index.ts` | 路由定义 |
| 8 | `frontend/src/types/index.ts` | TypeScript 类型 |
| 9 | `frontend/src/api/client.ts` | Axios 实例 |
| 10 | `frontend/src/api/models.ts` | 模型 API |
| 11 | `frontend/src/api/training.ts` | 训练 API |
| 12 | `frontend/src/api/evaluation.ts` | 评估 API |
| 13 | `frontend/src/api/publishing.ts` | 发布 API |
| 14 | `frontend/src/components/ModelSelector.vue` | 模型选择器组件 |
| 15 | `frontend/src/components/TaskStatusBadge.vue` | 状态标签组件 |
| 16 | `frontend/src/components/LogViewer.vue` | 日志查看器组件 |
| 17 | `frontend/src/views/ModelsView.vue` | 模型列表页 |
| 18 | `frontend/src/views/ModelDetailView.vue` | 模型详情页 |
| 19 | `frontend/src/views/TrainingView.vue` | 训练任务列表页 |
| 20 | `frontend/src/views/TrainingDetailView.vue` | 训练详情页 |
| 21 | `frontend/src/views/EvaluationView.vue` | 评估记录列表页 |
| 22 | `frontend/src/views/EvaluationDetailView.vue` | 评估详情页 |
| 23 | `frontend/src/views/PublishView.vue` | 发布管理页 |

---

### 任务 1：项目脚手架

**文件：**
- 创建：`AIStudio/frontend/package.json`
- 创建：`AIStudio/frontend/vite.config.ts`
- 创建：`AIStudio/frontend/tsconfig.json`
- 创建：`AIStudio/frontend/tsconfig.node.json`
- 创建：`AIStudio/frontend/index.html`
- 创建：`AIStudio/frontend/src/main.ts`
- 创建：`AIStudio/frontend/env.d.ts`

- [ ] **步骤 1：创建 package.json**

`AIStudio/frontend/package.json`:
```json
{
  "name": "aistudio-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "naive-ui": "^2.40.0",
    "axios": "^1.6.0",
    "@vicons/ionicons5": "^0.12.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.0.0"
  }
}
```

- [ ] **步骤 2：创建 vite.config.ts**

`AIStudio/frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **步骤 3：创建 tsconfig.json**

`AIStudio/frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForExpose": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "baseUrl": "."
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue", "env.d.ts"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

`AIStudio/frontend/tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **步骤 4：创建 index.html**

`AIStudio/frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AIStudio - AI 工作流平台</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **步骤 5：创建 Vue 入口**

`AIStudio/frontend/env.d.ts`:
```typescript
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

`AIStudio/frontend/src/main.ts`:
```typescript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')
```

- [ ] **步骤 6：安装依赖并验证**

运行：`cd AIStudio/frontend && npm install`
预期：依赖安装完成无错误

- [ ] **步骤 7：Commit**

```bash
git add AIStudio/frontend/package.json AIStudio/frontend/vite.config.ts AIStudio/frontend/tsconfig.json AIStudio/frontend/tsconfig.node.json AIStudio/frontend/index.html AIStudio/frontend/src/main.ts AIStudio/frontend/env.d.ts
git commit -m "feat: add frontend scaffolding - Vite + Vue3 + TypeScript"
```

---

### 任务 2：TypeScript 类型定义

**文件：**
- 创建：`AIStudio/frontend/src/types/index.ts`

- [ ] **步骤 1：编写类型定义**

`AIStudio/frontend/src/types/index.ts`:
```typescript
// ====== Model ======
export type ModelSource = 'huggingface' | 'local' | 'uploaded'
export type ModelType = 'llm' | 'embedding' | 'peft_checkpoint'
export type ModelStatus = 'downloading' | 'ready' | 'error'

export interface Model {
  id: number
  name: string
  source: ModelSource
  source_path: string
  model_type: ModelType
  base_model_id: number | null
  status: ModelStatus
  local_path: string
  description: string
  created_at: string
  updated_at: string
}

export interface ModelListResponse {
  models: Model[]
  total: number
}

export interface ModelCreatePayload {
  name: string
  source: ModelSource
  source_path: string
  model_type: ModelType
  base_model_id?: number | null
  description?: string
}

// ====== Training ======
export type TrainingMethod = 'lora' | 'qlora'
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface TrainingTask {
  id: number
  model_id: number
  method: TrainingMethod
  config: Record<string, any>
  status: TaskStatus
  pid: number | null
  log_path: string
  output_model_id: number | null
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface TrainingListResponse {
  tasks: TrainingTask[]
  total: number
}

export interface TrainingConfig {
  method: TrainingMethod
  learning_rate: number
  num_epochs: number
  batch_size: number
  lora_r: number
  lora_alpha: number
  max_length: number
  dataset_path: string
  output_name: string
}

export interface TrainingCreatePayload {
  model_id: number
  config: TrainingConfig
}

// ====== Evaluation ======
export type EvalType = 'perplexity' | 'benchmark' | 'custom'
export type EvalStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface EvaluationRecord {
  id: number
  model_id: number
  eval_type: EvalType
  dataset: string
  metrics: Record<string, any> | null
  status: EvalStatus
  log_path: string
  error_message: string | null
  created_at: string
}

export interface EvaluationListResponse {
  records: EvaluationRecord[]
  total: number
}

export interface EvaluationCreatePayload {
  model_id: number
  eval_type: EvalType
  dataset: string
}

// ====== Publishing ======
export type ServiceType = 'api' | 'export'
export type ServiceStatus = 'running' | 'stopped' | 'failed'

export interface PublishedService {
  id: number
  model_id: number
  service_type: ServiceType
  endpoint: string | null
  export_path: string | null
  config: Record<string, any>
  status: ServiceStatus
  pid: number | null
  error_message: string | null
  created_at: string
  stopped_at: string | null
}

export interface PublishListResponse {
  services: PublishedService[]
  total: number
}

export interface PublishCreatePayload {
  model_id: number
  service_type: ServiceType
  config: Record<string, any>
}

// ====== Common ======
export interface LogResponse {
  logs: string
}
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/frontend/src/types/index.ts
git commit -m "feat: add TypeScript type definitions"
```

---

### 任务 3：API 客户端层

**文件：**
- 创建：`AIStudio/frontend/src/api/client.ts`
- 创建：`AIStudio/frontend/src/api/models.ts`
- 创建：`AIStudio/frontend/src/api/training.ts`
- 创建：`AIStudio/frontend/src/api/evaluation.ts`
- 创建：`AIStudio/frontend/src/api/publishing.ts`

- [ ] **步骤 1：编写 Axios 客户端**

`AIStudio/frontend/src/api/client.ts`:
```typescript
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export default client
```

- [ ] **步骤 2：编写模型 API**

`AIStudio/frontend/src/api/models.ts`:
```typescript
import client from './client'
import type {
  Model,
  ModelListResponse,
  ModelCreatePayload,
} from '../types'

export async function listModels(
  modelType?: string,
  status?: string
): Promise<ModelListResponse> {
  const params: Record<string, string> = {}
  if (modelType) params.model_type = modelType
  if (status) params.status = status
  const { data } = await client.get<ModelListResponse>('/models', { params })
  return data
}

export async function getModel(id: number): Promise<Model> {
  const { data } = await client.get<Model>(`/models/${id}`)
  return data
}

export async function createModel(payload: ModelCreatePayload): Promise<Model> {
  const { data } = await client.post<Model>('/models', payload)
  return data
}

export async function deleteModel(id: number): Promise<void> {
  await client.delete(`/models/${id}`)
}

export async function downloadModel(id: number): Promise<{ status: string }> {
  const { data } = await client.post<{ status: string }>(`/models/${id}/download`)
  return data
}
```

- [ ] **步骤 3：编写训练 API**

`AIStudio/frontend/src/api/training.ts`:
```typescript
import client from './client'
import type {
  TrainingTask,
  TrainingListResponse,
  TrainingCreatePayload,
  LogResponse,
} from '../types'

export async function listTrainingTasks(status?: string): Promise<TrainingListResponse> {
  const params: Record<string, string> = {}
  if (status) params.status = status
  const { data } = await client.get<TrainingListResponse>('/training', { params })
  return data
}

export async function getTrainingTask(id: number): Promise<TrainingTask> {
  const { data } = await client.get<TrainingTask>(`/training/${id}`)
  return data
}

export async function createTrainingTask(payload: TrainingCreatePayload): Promise<TrainingTask> {
  const { data } = await client.post<TrainingTask>('/training', payload)
  return data
}

export async function cancelTrainingTask(id: number): Promise<void> {
  await client.post(`/training/${id}/cancel`)
}

export async function getTrainingLogs(id: number): Promise<LogResponse> {
  const { data } = await client.get<LogResponse>(`/training/${id}/logs`)
  return data
}
```

- [ ] **步骤 4：编写评估 API**

`AIStudio/frontend/src/api/evaluation.ts`:
```typescript
import client from './client'
import type {
  EvaluationRecord,
  EvaluationListResponse,
  EvaluationCreatePayload,
  LogResponse,
} from '../types'

export async function listEvaluations(status?: string): Promise<EvaluationListResponse> {
  const params: Record<string, string> = {}
  if (status) params.status = status
  const { data } = await client.get<EvaluationListResponse>('/evaluation', { params })
  return data
}

export async function getEvaluation(id: number): Promise<EvaluationRecord> {
  const { data } = await client.get<EvaluationRecord>(`/evaluation/${id}`)
  return data
}

export async function createEvaluation(payload: EvaluationCreatePayload): Promise<EvaluationRecord> {
  const { data } = await client.post<EvaluationRecord>('/evaluation', payload)
  return data
}

export async function deleteEvaluation(id: number): Promise<void> {
  await client.delete(`/evaluation/${id}`)
}

export async function getEvaluationLogs(id: number): Promise<LogResponse> {
  const { data } = await client.get<LogResponse>(`/evaluation/${id}/logs`)
  return data
}
```

- [ ] **步骤 5：编写发布 API**

`AIStudio/frontend/src/api/publishing.ts`:
```typescript
import client from './client'
import type {
  PublishedService,
  PublishListResponse,
  PublishCreatePayload,
} from '../types'

export async function listServices(): Promise<PublishListResponse> {
  const { data } = await client.get<PublishListResponse>('/publishing')
  return data
}

export async function getService(id: number): Promise<PublishedService> {
  const { data } = await client.get<PublishedService>(`/publishing/${id}`)
  return data
}

export async function createService(payload: PublishCreatePayload): Promise<PublishedService> {
  const { data } = await client.post<PublishedService>('/publishing', payload)
  return data
}

export async function stopService(id: number): Promise<void> {
  await client.post(`/publishing/${id}/stop`)
}

export async function deleteService(id: number): Promise<void> {
  await client.delete(`/publishing/${id}`)
}
```

- [ ] **步骤 6：Commit**

```bash
git add AIStudio/frontend/src/api/
git commit -m "feat: add API client layer - models, training, evaluation, publishing"
```

---

### 任务 4：路由与布局

**文件：**
- 创建：`AIStudio/frontend/src/router/index.ts`
- 创建：`AIStudio/frontend/src/App.vue`

- [ ] **步骤 1：编写路由配置**

`AIStudio/frontend/src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/models' },
    {
      path: '/models',
      name: 'models',
      component: () => import('../views/ModelsView.vue'),
    },
    {
      path: '/models/:id',
      name: 'model-detail',
      component: () => import('../views/ModelDetailView.vue'),
    },
    {
      path: '/training',
      name: 'training',
      component: () => import('../views/TrainingView.vue'),
    },
    {
      path: '/training/:id',
      name: 'training-detail',
      component: () => import('../views/TrainingDetailView.vue'),
    },
    {
      path: '/evaluation',
      name: 'evaluation',
      component: () => import('../views/EvaluationView.vue'),
    },
    {
      path: '/evaluation/:id',
      name: 'evaluation-detail',
      component: () => import('../views/EvaluationDetailView.vue'),
    },
    {
      path: '/publishing',
      name: 'publishing',
      component: () => import('../views/PublishView.vue'),
    },
  ],
})

export default router
```

- [ ] **步骤 2：编写 App.vue（主布局）**

`AIStudio/frontend/src/App.vue`:
```vue
<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="200"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="logo">
        <n-icon size="28" v-if="collapsed">
          <flash-outline />
        </n-icon>
        <span v-else style="font-weight: 700; font-size: 18px">AIStudio</span>
      </div>
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :value="activeKey"
        :options="menuOptions"
        @update:value="handleMenuSelect"
      />
    </n-layout-sider>
    <n-layout>
      <n-layout-content style="padding: 24px; overflow-y: auto">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon, NLayout, NLayoutSider, NMenu } from 'naive-ui'
import {
  CubeOutline,
  FlashOutline,
  FlaskOutline,
  RocketOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const activeKey = computed(() => route.path)

interface MenuOption {
  label: string
  key: string
  icon: () => any
}

const menuOptions: MenuOption[] = [
  {
    label: '模型管理',
    key: '/models',
    icon: () => h(NIcon, null, { default: () => h(CubeOutline) }),
  },
  {
    label: '模型训练',
    key: '/training',
    icon: () => h(NIcon, null, { default: () => h(FlashOutline) }),
  },
  {
    label: '模型评估',
    key: '/evaluation',
    icon: () => h(NIcon, null, { default: () => h(FlaskOutline) }),
  },
  {
    label: '模型发布',
    key: '/publishing',
    icon: () => h(NIcon, null, { default: () => h(RocketOutline) }),
  },
]

function handleMenuSelect(key: string) {
  router.push(key)
}
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64px;
  border-bottom: 1px solid #efefef;
}
</style>
```

- [ ] **步骤 3：Commit**

```bash
git add AIStudio/frontend/src/router/index.ts AIStudio/frontend/src/App.vue
git commit -m "feat: add router config and main layout with navigation"
```

---

### 任务 5：核心组件

**文件：**
- 创建：`AIStudio/frontend/src/components/ModelSelector.vue`
- 创建：`AIStudio/frontend/src/components/TaskStatusBadge.vue`
- 创建：`AIStudio/frontend/src/components/LogViewer.vue`

- [ ] **步骤 1：编写 ModelSelector**

`AIStudio/frontend/src/components/ModelSelector.vue`:
```vue
<template>
  <n-select
    :value="modelValue"
    :options="options"
    :loading="loading"
    placeholder="选择模型"
    filterable
    @update:value="emit('update:modelValue', $event)"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { NSelect } from 'naive-ui'
import { listModels } from '../api/models'
import type { Model } from '../types'

const props = defineProps<{
  modelValue: number | null
  modelType?: string
  onlyReady?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
}>()

const loading = ref(false)
const models = ref<Model[]>([])

const options = computed(() =>
  models.value.map((m) => ({
    label: `${m.name} (${m.model_type})`,
    value: m.id,
  }))
)

async function fetchModels() {
  loading.value = true
  try {
    const resp = await listModels(
      props.modelType,
      props.onlyReady ? 'ready' : undefined
    )
    models.value = resp.models
  } catch (e) {
    models.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchModels)
watch(() => props.modelType, fetchModels)
</script>
```

- [ ] **步骤 2：编写 TaskStatusBadge**

`AIStudio/frontend/src/components/TaskStatusBadge.vue`:
```vue
<template>
  <n-tag :type="tagType" size="small">
    {{ statusLabel }}
  </n-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NTag } from 'naive-ui'

const props = defineProps<{
  status: string
}>()

const statusMap: Record<string, { type: 'default' | 'info' | 'success' | 'error' | 'warning'; label: string }> = {
  ready: { type: 'success', label: '就绪' },
  downloading: { type: 'info', label: '下载中' },
  error: { type: 'error', label: '错误' },
  pending: { type: 'default', label: '等待中' },
  running: { type: 'info', label: '运行中' },
  completed: { type: 'success', label: '已完成' },
  failed: { type: 'error', label: '失败' },
  cancelled: { type: 'warning', label: '已取消' },
  stopped: { type: 'default', label: '已停止' },
}

const tagType = computed(() => statusMap[props.status]?.type ?? 'default')
const statusLabel = computed(() => statusMap[props.status]?.label ?? props.status)
</script>
```

- [ ] **步骤 3：编写 LogViewer**

`AIStudio/frontend/src/components/LogViewer.vue`:
```vue
<template>
  <div class="log-viewer">
    <div class="log-header">
      <span class="log-title">日志输出</span>
      <n-space size="small">
        <n-button size="tiny" @click="toggleAutoScroll">
          {{ autoScroll ? '暂停滚动' : '自动滚动' }}
        </n-button>
        <n-button size="tiny" @click="refresh">刷新</n-button>
      </n-space>
    </div>
    <n-input
      ref="logRef"
      type="textarea"
      :value="logs"
      readonly
      :rows="15"
      style="font-family: monospace; font-size: 12px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { NButton, NSpace, NInput } from 'naive-ui'

const props = defineProps<{
  logs: string
  loading?: boolean
}>()

const emit = defineEmits<{
  refresh: []
}>()

const autoScroll = ref(true)
const logRef = ref<InstanceType<typeof NInput> | null>(null)

function toggleAutoScroll() {
  autoScroll.value = !autoScroll.value
}

function refresh() {
  emit('refresh')
}

watch(
  () => props.logs,
  async () => {
    if (autoScroll.value) {
      await nextTick()
      const textarea = logRef.value?.$el?.querySelector('textarea')
      if (textarea) {
        textarea.scrollTop = textarea.scrollHeight
      }
    }
  }
)
</script>

<style scoped>
.log-viewer {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}
.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}
.log-title {
  font-weight: 600;
  font-size: 13px;
}
</style>
```

- [ ] **步骤 4：Commit**

```bash
git add AIStudio/frontend/src/components/
git commit -m "feat: add core components - ModelSelector, TaskStatusBadge, LogViewer"
```

---

### 任务 6：模型管理视图

**文件：**
- 创建：`AIStudio/frontend/src/views/ModelsView.vue`

- [ ] **步骤 1：编写 ModelsView**

`AIStudio/frontend/src/views/ModelsView.vue`:
```vue
<template>
  <div>
    <n-page-header>
      <template #title>模型管理</template>
      <template #extra>
        <n-button type="primary" @click="showCreateModal = true">
          导入模型
        </n-button>
      </template>
    </n-page-header>

    <n-data-table
      :columns="columns"
      :data="models"
      :loading="loading"
      :pagination="{ pageSize: 20 }"
      style="margin-top: 16px"
    />

    <!-- Import modal -->
    <n-modal v-model:show="showCreateModal" preset="card" title="导入模型" style="width: 520px">
      <n-form ref="formRef" :model="formData" label-placement="top">
        <n-form-item label="模型名称" path="name" :rule="[{ required: true }]">
          <n-input v-model:value="formData.name" placeholder="如 Qwen2.5-7B" />
        </n-form-item>
        <n-form-item label="来源" path="source">
          <n-radio-group v-model:value="formData.source">
            <n-radio value="huggingface">HuggingFace</n-radio>
            <n-radio value="local">本地路径</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item
          :label="formData.source === 'huggingface' ? 'HF 模型 ID' : '本地路径'"
          path="source_path"
          :rule="[{ required: true }]"
        >
          <n-input
            v-model:value="formData.source_path"
            :placeholder="formData.source === 'huggingface' ? 'Qwen/Qwen2.5-7B' : '/path/to/model'"
          />
        </n-form-item>
        <n-form-item label="模型类型" path="model_type">
          <n-radio-group v-model:value="formData.model_type">
            <n-radio value="llm">大语言模型 (LLM)</n-radio>
            <n-radio value="embedding">Embedding 模型</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="备注" path="description">
          <n-input v-model:value="formData.description" type="textarea" :rows="2" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="handleCreate">
            确认导入
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NDataTable,
  NPageHeader,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NRadio,
  NRadioGroup,
  NSpace,
  useMessage,
} from 'naive-ui'
import { listModels, createModel, downloadModel, deleteModel } from '../api/models'
import type { Model, ModelCreatePayload } from '../types'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'

const router = useRouter()
const message = useMessage()

const models = ref<Model[]>([])
const loading = ref(false)
const creating = ref(false)
const showCreateModal = ref(false)

const formData = ref<ModelCreatePayload>({
  name: '',
  source: 'huggingface',
  source_path: '',
  model_type: 'llm',
  description: '',
})

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '类型',
    key: 'model_type',
    width: 130,
    render: (row: Model) =>
      ({ llm: 'LLM', embedding: 'Embedding', peft_checkpoint: 'LoRA 适配器' }[row.model_type] ?? row.model_type),
  },
  {
    title: '来源',
    key: 'source',
    width: 100,
    render: (row: Model) =>
      ({ huggingface: 'HF', local: '本地', uploaded: '上传' }[row.source] ?? row.source),
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: Model) => h(TaskStatusBadge, { status: row.status }),
  },
  { title: '来源路径', key: 'source_path', ellipsis: { tooltip: true } },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    render: (row: Model) =>
      h(NSpace, null, {
        default: () => [
          h(NButton, {
            size: 'tiny',
            onClick: () => router.push(`/models/${row.id}`),
          }, { default: () => '详情' }),
          row.source === 'huggingface' && row.status === 'ready'
            ? h(NButton, {
                size: 'tiny',
                onClick: () => handleDownload(row.id),
              }, { default: () => '下载' })
            : null,
          h(NButton, {
            size: 'tiny',
            type: 'error',
            onClick: () => handleDelete(row.id),
          }, { default: () => '删除' }),
        ].filter(Boolean),
      }),
  },
]

async function fetchModels() {
  loading.value = true
  try {
    const resp = await listModels()
    models.value = resp.models
  } catch (e: any) {
    message.error('获取模型列表失败: ' + (e?.message || ''))
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!formData.value.name || !formData.value.source_path) {
    message.warning('请填写名称和来源路径')
    return
  }
  creating.value = true
  try {
    await createModel(formData.value)
    message.success('模型导入成功')
    showCreateModal.value = false
    formData.value = { name: '', source: 'huggingface', source_path: '', model_type: 'llm', description: '' }
    await fetchModels()
  } catch (e: any) {
    message.error('导入失败: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally {
    creating.value = false
  }
}

async function handleDownload(id: number) {
  try {
    await downloadModel(id)
    message.success('已启动下载')
    await fetchModels()
  } catch (e: any) {
    message.error('下载失败: ' + (e?.message || ''))
  }
}

async function handleDelete(id: number) {
  try {
    await deleteModel(id)
    message.success('已删除')
    await fetchModels()
  } catch (e: any) {
    message.error('删除失败: ' + (e?.response?.data?.detail || e?.message || ''))
  }
}

onMounted(fetchModels)
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/frontend/src/views/ModelsView.vue
git commit -m "feat: add ModelsView - model list, import, delete, download"
```

---

### 任务 7：模型详情视图

**文件：**
- 创建：`AIStudio/frontend/src/views/ModelDetailView.vue`

- [ ] **步骤 1：编写 ModelDetailView**

`AIStudio/frontend/src/views/ModelDetailView.vue`:
```vue
<template>
  <div v-if="model">
    <n-page-header>
      <template #title>{{ model.name }}</template>
      <template #extra>
        <n-button @click="router.push('/models')">返回列表</n-button>
      </template>
    </n-page-header>

    <n-card title="基本信息" style="margin-top: 16px">
      <n-descriptions label-placement="left" :column="2">
        <n-descriptions-item label="ID">{{ model.id }}</n-descriptions-item>
        <n-descriptions-item label="名称">{{ model.name }}</n-descriptions-item>
        <n-descriptions-item label="类型">{{ model.model_type }}</n-descriptions-item>
        <n-descriptions-item label="来源">{{ model.source }}</n-descriptions-item>
        <n-descriptions-item label="来源路径">{{ model.source_path }}</n-descriptions-item>
        <n-descriptions-item label="本地路径">{{ model.local_path || '-' }}</n-descriptions-item>
        <n-descriptions-item label="状态">
          <task-status-badge :status="model.status" />
        </n-descriptions-item>
        <n-descriptions-item label="备注">{{ model.description || '-' }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card title="操作" style="margin-top: 16px">
      <n-space>
        <n-button type="primary" @click="goToTraining">
          发起训练
        </n-button>
        <n-button type="primary" @click="goToEvaluation">
          发起评估
        </n-button>
        <n-button type="primary" @click="goToPublish">
          发布模型
        </n-button>
        <n-button v-if="model.source === 'huggingface' && model.status === 'ready'" @click="handleDownload">
          下载模型
        </n-button>
        <n-button type="error" @click="handleDelete">
          删除模型
        </n-button>
      </n-space>
    </n-card>

    <!-- Training tasks of this model -->
    <n-card title="训练任务" style="margin-top: 16px">
      <n-data-table
        :columns="taskColumns"
        :data="trainingTasks"
        :loading="tasksLoading"
        :pagination="{ pageSize: 5 }"
      />
    </n-card>

    <!-- Evaluation records of this model -->
    <n-card title="评估记录" style="margin-top: 16px">
      <n-data-table
        :columns="evalColumns"
        :data="evalRecords"
        :loading="evalLoading"
        :pagination="{ pageSize: 5 }"
      />
    </n-card>
  </div>
  <n-spin v-else size="large" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NPageHeader,
  NSpace,
  NSpin,
  useMessage,
} from 'naive-ui'
import { getModel, downloadModel, deleteModel } from '../api/models'
import { listTrainingTasks } from '../api/training'
import { listEvaluations } from '../api/evaluation'
import type { Model, TrainingTask, EvaluationRecord } from '../types'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const modelId = Number(route.params.id)

const model = ref<Model | null>(null)
const trainingTasks = ref<TrainingTask[]>([])
const evalRecords = ref<EvaluationRecord[]>([])
const tasksLoading = ref(false)
const evalLoading = ref(false)

const taskColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '方法', key: 'method', width: 80 },
  {
    title: '状态', key: 'status', width: 100,
    render: (row: TrainingTask) => h(TaskStatusBadge, { status: row.status }),
  },
  { title: '开始时间', key: 'started_at' },
  {
    title: '操作', key: 'actions', width: 80,
    render: (row: TrainingTask) => h(NButton, {
      size: 'tiny',
      onClick: () => router.push(`/training/${row.id}`),
    }, { default: () => '详情' }),
  },
]

const evalColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '类型', key: 'eval_type', width: 100 },
  {
    title: '状态', key: 'status', width: 100,
    render: (row: EvaluationRecord) => h(TaskStatusBadge, { status: row.status }),
  },
  { title: '创建时间', key: 'created_at' },
  {
    title: '操作', key: 'actions', width: 80,
    render: (row: EvaluationRecord) => h(NButton, {
      size: 'tiny',
      onClick: () => router.push(`/evaluation/${row.id}`),
    }, { default: () => '详情' }),
  },
]

function goToTraining() {
  router.push({ path: '/training', query: { modelId: String(modelId) } })
}

function goToEvaluation() {
  router.push({ path: '/evaluation', query: { modelId: String(modelId) } })
}

function goToPublish() {
  router.push({ path: '/publishing', query: { modelId: String(modelId) } })
}

async function handleDownload() {
  try {
    await downloadModel(modelId)
    message.success('已启动下载')
  } catch (e: any) {
    message.error('下载失败')
  }
}

async function handleDelete() {
  try {
    await deleteModel(modelId)
    message.success('已删除')
    router.push('/models')
  } catch (e: any) {
    message.error('删除失败: ' + (e?.response?.data?.detail || e?.message || ''))
  }
}

onMounted(async () => {
  try {
    model.value = await getModel(modelId)
  } catch {
    message.error('模型不存在')
    router.push('/models')
    return
  }
  tasksLoading.value = true
  try {
    const resp = await listTrainingTasks()
    trainingTasks.value = resp.tasks.filter((t) => t.model_id === modelId)
  } finally {
    tasksLoading.value = false
  }
  evalLoading.value = true
  try {
    const resp = await listEvaluations()
    evalRecords.value = resp.records.filter((r) => r.model_id === modelId)
  } finally {
    evalLoading.value = false
  }
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/frontend/src/views/ModelDetailView.vue
git commit -m "feat: add ModelDetailView - model info, operations, related tasks"
```

---

### 任务 8：训练视图

**文件：**
- 创建：`AIStudio/frontend/src/views/TrainingView.vue`
- 创建：`AIStudio/frontend/src/views/TrainingDetailView.vue`

- [ ] **步骤 1：编写 TrainingView**

`AIStudio/frontend/src/views/TrainingView.vue`:
```vue
<template>
  <div>
    <n-page-header>
      <template #title>模型训练</template>
      <template #extra>
        <n-button type="primary" @click="showCreate = true">新建训练</n-button>
      </template>
    </n-page-header>

    <n-data-table
      :columns="columns"
      :data="tasks"
      :loading="loading"
      :pagination="{ pageSize: 20 }"
      style="margin-top: 16px"
    />

    <n-modal v-model:show="showCreate" preset="card" title="新建训练任务" style="width: 600px">
      <n-form label-placement="top">
        <n-form-item label="选择模型" required>
          <model-selector
            v-model="form.modelId"
            :model-type="'llm'"
            :only-ready="true"
          />
        </n-form-item>
        <n-form-item label="训练方法" required>
          <n-radio-group v-model:value="form.method">
            <n-radio value="lora">LoRA</n-radio>
            <n-radio value="qlora">QLoRA</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="数据集路径">
          <n-input v-model:value="form.datasetPath" placeholder="/path/to/train.jsonl" />
        </n-form-item>
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="学习率">
              <n-input-number v-model:value="form.learningRate" :min="1e-6" :max="1" :step="1e-5" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="训练轮数">
              <n-input-number v-model:value="form.epochs" :min="1" :max="100" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Batch Size">
              <n-input-number v-model:value="form.batchSize" :min="1" :max="64" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="最大长度">
              <n-input-number v-model:value="form.maxLength" :min="64" :max="8192" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="LoRA r">
              <n-input-number v-model:value="form.loraR" :min="1" :max="128" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="LoRA alpha">
              <n-input-number v-model:value="form.loraAlpha" :min="1" :max="256" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item label="输出名称">
          <n-input v-model:value="form.outputName" placeholder="留空自动生成" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="handleCreate">开始训练</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NDataTable, NPageHeader, NModal, NForm, NFormItem,
  NInput, NInputNumber, NRadio, NRadioGroup, NGrid, NGridItem,
  NSpace, useMessage,
} from 'naive-ui'
import { listTrainingTasks, createTrainingTask } from '../api/training'
import type { TrainingTask } from '../types'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import ModelSelector from '../components/ModelSelector.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const tasks = ref<TrainingTask[]>([])
const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)

const form = ref({
  modelId: null as number | null,
  method: 'lora' as 'lora' | 'qlora',
  datasetPath: '',
  learningRate: 2e-4,
  epochs: 3,
  batchSize: 4,
  maxLength: 512,
  loraR: 8,
  loraAlpha: 32,
  outputName: '',
})

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '模型 ID', key: 'model_id', width: 80 },
  { title: '方法', key: 'method', width: 70 },
  {
    title: '状态', key: 'status', width: 100,
    render: (row: TrainingTask) => h(TaskStatusBadge, { status: row.status }),
  },
  { title: '开始时间', key: 'started_at', width: 180 },
  { title: '完成时间', key: 'finished_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 120,
    render: (row: TrainingTask) => h(NSpace, null, {
      default: () => [
        h(NButton, {
          size: 'tiny',
          onClick: () => router.push(`/training/${row.id}`),
        }, { default: () => '详情' }),
        row.status === 'running'
          ? h(NButton, { size: 'tiny', type: 'warning', onClick: () => handleCancel(row.id) },
              { default: () => '取消' })
          : null,
      ],
    }),
  },
]

async function fetchTasks() {
  loading.value = true
  try {
    const resp = await listTrainingTasks()
    tasks.value = resp.tasks
  } catch {
    message.error('获取训练任务列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.modelId) {
    message.warning('请选择模型')
    return
  }
  creating.value = true
  try {
    await createTrainingTask({
      model_id: form.value.modelId,
      config: {
        method: form.value.method,
        learning_rate: form.value.learningRate,
        num_epochs: form.value.epochs,
        batch_size: form.value.batchSize,
        lora_r: form.value.loraR,
        lora_alpha: form.value.loraAlpha,
        max_length: form.value.maxLength,
        dataset_path: form.value.datasetPath,
        output_name: form.value.outputName,
      },
    })
    message.success('训练任务已创建')
    showCreate.value = false
    await fetchTasks()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally {
    creating.value = false
  }
}

async function handleCancel(id: number) {
  try {
    const { cancelTrainingTask } = await import('../api/training')
    await cancelTrainingTask(id)
    message.success('已取消')
    await fetchTasks()
  } catch (e: any) {
    message.error('取消失败')
  }
}

onMounted(() => {
  fetchTasks()
  // Pre-select model if passed via query
  const modelId = route.query.modelId
  if (modelId) {
    form.value.modelId = Number(modelId)
    showCreate.value = true
  }
})
</script>
```

- [ ] **步骤 2：编写 TrainingDetailView**

`AIStudio/frontend/src/views/TrainingDetailView.vue`:
```vue
<template>
  <div v-if="task">
    <n-page-header>
      <template #title>训练任务 #{{ task.id }}</template>
      <template #extra>
        <n-button @click="router.push('/training')">返回列表</n-button>
      </template>
    </n-page-header>

    <n-card title="任务信息" style="margin-top: 16px">
      <n-descriptions label-placement="left" :column="2">
        <n-descriptions-item label="状态">
          <task-status-badge :status="task.status" />
        </n-descriptions-item>
        <n-descriptions-item label="方法">{{ task.method }}</n-descriptions-item>
        <n-descriptions-item label="模型 ID">{{ task.model_id }}</n-descriptions-item>
        <n-descriptions-item label="PID">{{ task.pid || '-' }}</n-descriptions-item>
        <n-descriptions-item label="开始时间">{{ task.started_at || '-' }}</n-descriptions-item>
        <n-descriptions-item label="结束时间">{{ task.finished_at || '-' }}</n-descriptions-item>
        <n-descriptions-item label="产出模型 ID">{{ task.output_model_id || '-' }}</n-descriptions-item>
        <n-descriptions-item v-if="task.error_message" label="错误信息" :span="2">
          <n-text type="error">{{ task.error_message }}</n-text>
        </n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card title="超参配置" style="margin-top: 16px" v-if="task.config">
      <n-code :code="JSON.stringify(task.config, null, 2)" language="json" />
    </n-card>

    <n-card style="margin-top: 16px">
      <log-viewer :logs="logs" :loading="logLoading" @refresh="fetchLogs" />
    </n-card>
  </div>
  <n-spin v-else size="large" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NCard, NCode, NDescriptions, NDescriptionsItem,
  NPageHeader, NSpin, NText, useMessage,
} from 'naive-ui'
import { getTrainingTask, getTrainingLogs } from '../api/training'
import type { TrainingTask } from '../types'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import LogViewer from '../components/LogViewer.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const taskId = Number(route.params.id)

const task = ref<TrainingTask | null>(null)
const logs = ref('')
const logLoading = ref(false)

async function fetchTask() {
  try {
    task.value = await getTrainingTask(taskId)
  } catch {
    message.error('任务不存在')
    router.push('/training')
  }
}

async function fetchLogs() {
  logLoading.value = true
  try {
    const resp = await getTrainingLogs(taskId)
    logs.value = resp.logs
  } catch {
    logs.value = '无法获取日志'
  } finally {
    logLoading.value = false
  }
}

onMounted(async () => {
  await fetchTask()
  await fetchLogs()
  // Auto refresh logs every 3s while running
  if (task.value?.status === 'running') {
    setInterval(fetchLogs, 3000)
  }
})
</script>
```

- [ ] **步骤 3：Commit**

```bash
git add AIStudio/frontend/src/views/TrainingView.vue AIStudio/frontend/src/views/TrainingDetailView.vue
git commit -m "feat: add TrainingView and TrainingDetailView"
```

---

### 任务 9：评估视图

**文件：**
- 创建：`AIStudio/frontend/src/views/EvaluationView.vue`
- 创建：`AIStudio/frontend/src/views/EvaluationDetailView.vue`

- [ ] **步骤 1：编写 EvaluationView**

`AIStudio/frontend/src/views/EvaluationView.vue`:
```vue
<template>
  <div>
    <n-page-header>
      <template #title>模型评估</template>
      <template #extra>
        <n-button type="primary" @click="showCreate = true">新建评估</n-button>
      </template>
    </n-page-header>

    <n-data-table
      :columns="columns"
      :data="records"
      :loading="loading"
      :pagination="{ pageSize: 20 }"
      style="margin-top: 16px"
    />

    <n-modal v-model:show="showCreate" preset="card" title="新建评估" style="width: 480px">
      <n-form label-placement="top">
        <n-form-item label="选择模型" required>
          <model-selector v-model="form.modelId" :only-ready="true" />
        </n-form-item>
        <n-form-item label="评估类型" required>
          <n-select
            v-model:value="form.evalType"
            :options="[
              { label: '困惑度 (Perplexity)', value: 'perplexity' },
              { label: '基准测试 (Benchmark)', value: 'benchmark' },
              { label: '自定义', value: 'custom' },
            ]"
          />
        </n-form-item>
        <n-form-item label="数据集路径">
          <n-input v-model:value="form.dataset" placeholder="/path/to/eval_data.jsonl" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="handleCreate">开始评估</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NDataTable, NPageHeader, NModal, NForm, NFormItem,
  NInput, NSelect, NSpace, useMessage,
} from 'naive-ui'
import { listEvaluations, createEvaluation } from '../api/evaluation'
import type { EvaluationRecord } from '../types'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import ModelSelector from '../components/ModelSelector.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const records = ref<EvaluationRecord[]>([])
const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)

const form = ref({
  modelId: null as number | null,
  evalType: 'perplexity' as 'perplexity' | 'benchmark' | 'custom',
  dataset: '',
})

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '模型 ID', key: 'model_id', width: 80 },
  { title: '类型', key: 'eval_type', width: 100 },
  {
    title: '状态', key: 'status', width: 100,
    render: (row: EvaluationRecord) => h(TaskStatusBadge, { status: row.status }),
  },
  { title: '数据集', key: 'dataset', ellipsis: { tooltip: true } },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 80,
    render: (row: EvaluationRecord) => h(NButton, {
      size: 'tiny',
      onClick: () => router.push(`/evaluation/${row.id}`),
    }, { default: () => '详情' }),
  },
]

async function fetchRecords() {
  loading.value = true
  try {
    const resp = await listEvaluations()
    records.value = resp.records
  } catch {
    message.error('获取评估列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.modelId) {
    message.warning('请选择模型')
    return
  }
  creating.value = true
  try {
    await createEvaluation({
      model_id: form.value.modelId,
      eval_type: form.value.evalType,
      dataset: form.value.dataset,
    })
    message.success('评估已创建')
    showCreate.value = false
    form.value = { modelId: null, evalType: 'perplexity', dataset: '' }
    await fetchRecords()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  fetchRecords()
  const modelId = route.query.modelId
  if (modelId) {
    form.value.modelId = Number(modelId)
    showCreate.value = true
  }
})
</script>
```

- [ ] **步骤 2：编写 EvaluationDetailView**

`AIStudio/frontend/src/views/EvaluationDetailView.vue`:
```vue
<template>
  <div v-if="record">
    <n-page-header>
      <template #title>评估记录 #{{ record.id }}</template>
      <template #extra>
        <n-button @click="router.push('/evaluation')">返回列表</n-button>
      </template>
    </n-page-header>

    <n-card title="评估信息" style="margin-top: 16px">
      <n-descriptions label-placement="left" :column="2">
        <n-descriptions-item label="状态">
          <task-status-badge :status="record.status" />
        </n-descriptions-item>
        <n-descriptions-item label="评估类型">{{ record.eval_type }}</n-descriptions-item>
        <n-descriptions-item label="模型 ID">{{ record.model_id }}</n-descriptions-item>
        <n-descriptions-item label="数据集">{{ record.dataset || '-' }}</n-descriptions-item>
        <n-descriptions-item label="创建时间">{{ record.created_at }}</n-descriptions-item>
        <n-descriptions-item v-if="record.error_message" label="错误信息" :span="2">
          <n-text type="error">{{ record.error_message }}</n-text>
        </n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card v-if="record.metrics" title="评估指标" style="margin-top: 16px">
      <n-descriptions label-placement="left" :column="2">
        <n-descriptions-item
          v-for="(value, key) in record.metrics"
          :key="key"
          :label="key"
        >
          {{ typeof value === 'number' ? value.toFixed(4) : value }}
        </n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card style="margin-top: 16px">
      <log-viewer :logs="logs" :loading="logLoading" @refresh="fetchLogs" />
    </n-card>
  </div>
  <n-spin v-else size="large" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NCard, NDescriptions, NDescriptionsItem,
  NPageHeader, NSpin, NText, useMessage,
} from 'naive-ui'
import { getEvaluation, getEvaluationLogs } from '../api/evaluation'
import type { EvaluationRecord } from '../types'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import LogViewer from '../components/LogViewer.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const recordId = Number(route.params.id)

const record = ref<EvaluationRecord | null>(null)
const logs = ref('')
const logLoading = ref(false)

async function fetchRecord() {
  try {
    record.value = await getEvaluation(recordId)
  } catch {
    message.error('评估记录不存在')
    router.push('/evaluation')
  }
}

async function fetchLogs() {
  logLoading.value = true
  try {
    const resp = await getEvaluationLogs(recordId)
    logs.value = resp.logs
  } catch {
    logs.value = '无法获取日志'
  } finally {
    logLoading.value = false
  }
}

onMounted(async () => {
  await fetchRecord()
  await fetchLogs()
  if (record.value?.status === 'running') {
    setInterval(fetchLogs, 3000)
  }
})
</script>
```

- [ ] **步骤 3：Commit**

```bash
git add AIStudio/frontend/src/views/EvaluationView.vue AIStudio/frontend/src/views/EvaluationDetailView.vue
git commit -m "feat: add EvaluationView and EvaluationDetailView"
```

---

### 任务 10：发布视图

**文件：**
- 创建：`AIStudio/frontend/src/views/PublishView.vue`

- [ ] **步骤 1：编写 PublishView**

`AIStudio/frontend/src/views/PublishView.vue`:
```vue
<template>
  <div>
    <n-page-header>
      <template #title>模型发布</template>
      <template #extra>
        <n-button type="primary" @click="showCreate = true">新建发布</n-button>
      </template>
    </n-page-header>

    <n-data-table
      :columns="columns"
      :data="services"
      :loading="loading"
      :pagination="{ pageSize: 20 }"
      style="margin-top: 16px"
    />

    <n-modal v-model:show="showCreate" preset="card" title="新建发布" style="width: 520px">
      <n-form label-placement="top">
        <n-form-item label="选择模型" required>
          <model-selector v-model="form.modelId" :only-ready="true" />
        </n-form-item>
        <n-form-item label="发布类型" required>
          <n-radio-group v-model:value="form.serviceType">
            <n-radio value="api">API 服务</n-radio>
            <n-radio value="export">导出文件</n-radio>
          </n-radio-group>
        </n-form-item>

        <!-- API config -->
        <template v-if="form.serviceType === 'api'">
          <n-grid :cols="2" :x-gap="12">
            <n-grid-item>
              <n-form-item label="端口">
                <n-input-number v-model:value="form.port" :min="1024" :max="65535" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Max Tokens">
                <n-input-number v-model:value="form.maxTokens" :min="64" :max="32768" />
              </n-form-item>
            </n-grid-item>
          </n-grid>
        </template>

        <!-- Export config -->
        <template v-if="form.serviceType === 'export'">
          <n-form-item label="导出路径" required>
            <n-input v-model:value="form.exportPath" placeholder="/path/to/export" />
          </n-form-item>
        </template>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="handleCreate">确认发布</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  NButton, NDataTable, NPageHeader, NModal, NForm, NFormItem,
  NInput, NInputNumber, NRadio, NRadioGroup, NGrid, NGridItem,
  NSpace, NTag, useMessage,
} from 'naive-ui'
import { listServices, createService, stopService, deleteService } from '../api/publishing'
import type { PublishedService } from '../types'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import ModelSelector from '../components/ModelSelector.vue'

const route = useRoute()
const message = useMessage()

const services = ref<PublishedService[]>([])
const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)

const form = ref({
  modelId: null as number | null,
  serviceType: 'api' as 'api' | 'export',
  port: 8300,
  maxTokens: 2048,
  exportPath: '',
})

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '模型 ID', key: 'model_id', width: 80 },
  {
    title: '类型', key: 'service_type', width: 80,
    render: (row: PublishedService) => row.service_type === 'api' ? 'API' : '导出',
  },
  {
    title: '状态', key: 'status', width: 100,
    render: (row: PublishedService) => h(TaskStatusBadge, { status: row.status }),
  },
  {
    title: '地址/路径', key: 'endpoint', ellipsis: { tooltip: true },
    render: (row: PublishedService) => row.service_type === 'api' ? row.endpoint : row.export_path,
  },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 200,
    render: (row: PublishedService) => h(NSpace, null, {
      default: () => [
        row.service_type === 'api' && row.status === 'running'
          ? h(NButton, {
              size: 'tiny',
              type: 'warning',
              onClick: () => handleStop(row.id),
            }, { default: () => '停止' })
          : null,
        h(NButton, {
          size: 'tiny',
          type: 'error',
          onClick: () => handleDelete(row.id),
        }, { default: () => '删除' }),
      ],
    }),
  },
]

async function fetchServices() {
  loading.value = true
  try {
    const resp = await listServices()
    services.value = resp.services
  } catch {
    message.error('获取发布列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.modelId) {
    message.warning('请选择模型')
    return
  }
  if (form.value.serviceType === 'export' && !form.value.exportPath) {
    message.warning('请填写导出路径')
    return
  }

  creating.value = true
  try {
    const config: Record<string, any> = {}
    if (form.value.serviceType === 'api') {
      config.port = form.value.port
      config.max_tokens = form.value.maxTokens
    } else {
      config.export_path = form.value.exportPath
    }

    await createService({
      model_id: form.value.modelId,
      service_type: form.value.serviceType,
      config,
    })
    message.success('发布已创建')
    showCreate.value = false
    await fetchServices()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally {
    creating.value = false
  }
}

async function handleStop(id: number) {
  try {
    await stopService(id)
    message.success('已停止')
    await fetchServices()
  } catch (e: any) {
    message.error('停止失败')
  }
}

async function handleDelete(id: number) {
  try {
    await deleteService(id)
    message.success('已删除')
    await fetchServices()
  } catch (e: any) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchServices()
  const modelId = route.query.modelId
  if (modelId) {
    form.value.modelId = Number(modelId)
    showCreate.value = true
  }
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add AIStudio/frontend/src/views/PublishView.vue
git commit -m "feat: add PublishView - API service and export management"
```

---

### 任务 11：验证前端构建

- [ ] **步骤 1：安装依赖**

运行：`cd AIStudio/frontend && npm install`
预期：依赖安装成功

- [ ] **步骤 2：启动 dev server**

运行：`cd AIStudio/frontend && npm run dev`
预期：Vite dev server 启动在 http://localhost:5173

- [ ] **步骤 3：在浏览器中确认**

打开 http://localhost:5173
预期：
- 左侧导航栏显示 4 个菜单（模型管理、模型训练、模型评估、模型发布）
- 默认跳转到 /models 页面
- "导入模型"按钮可点击打开对话框
- 无控制台报错

- [ ] **步骤 4：Commit**

```bash
git add -A
git commit -m "chore: finalize frontend setup and build verification"
```
