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
        <n-descriptions-item label="状态"><task-status-badge :status="model.status" /></n-descriptions-item>
        <n-descriptions-item label="备注">{{ model.description || '-' }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card title="操作" style="margin-top: 16px">
      <n-space>
        <n-button type="primary" @click="router.push({ path: '/training', query: { modelId: String(modelId) } })">发起训练</n-button>
        <n-button type="primary" @click="router.push({ path: '/evaluation', query: { modelId: String(modelId) } })">发起评估</n-button>
        <n-button type="primary" @click="router.push({ path: '/publishing', query: { modelId: String(modelId) } })">发布模型</n-button>
        <n-button v-if="model.source === 'huggingface' && model.status === 'ready'" @click="handleDownload">下载模型</n-button>
        <n-button type="error" @click="handleDelete">删除模型</n-button>
      </n-space>
    </n-card>

    <n-card title="训练任务" style="margin-top: 16px">
      <n-data-table :columns="taskColumns" :data="trainingTasks" :loading="tasksLoading" :pagination="{ pageSize: 5 }" />
    </n-card>

    <n-card title="评估记录" style="margin-top: 16px">
      <n-data-table :columns="evalColumns" :data="evalRecords" :loading="evalLoading" :pagination="{ pageSize: 5 }" />
    </n-card>
  </div>
  <n-spin v-else size="large" />
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NCard, NDataTable, NDescriptions, NDescriptionsItem,
  NPageHeader, NSpace, NSpin, useMessage,
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
  { title: '状态', key: 'status', width: 100, render: (row: TrainingTask) => h(TaskStatusBadge, { status: row.status }) },
  { title: '开始时间', key: 'started_at' },
  { title: '操作', key: 'actions', width: 80, render: (row: TrainingTask) => h(NButton, { size: 'tiny', onClick: () => router.push(`/training/${row.id}`) }, { default: () => '详情' }) },
]

const evalColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '类型', key: 'eval_type', width: 100 },
  { title: '状态', key: 'status', width: 100, render: (row: EvaluationRecord) => h(TaskStatusBadge, { status: row.status }) },
  { title: '创建时间', key: 'created_at' },
  { title: '操作', key: 'actions', width: 80, render: (row: EvaluationRecord) => h(NButton, { size: 'tiny', onClick: () => router.push(`/evaluation/${row.id}`) }, { default: () => '详情' }) },
]

async function handleDownload() {
  try { await downloadModel(modelId); message.success('已启动下载') } catch { message.error('下载失败') }
}

async function handleDelete() {
  try { await deleteModel(modelId); message.success('已删除'); router.push('/models') }
  catch (e: any) { message.error('删除失败: ' + (e?.response?.data?.detail || e?.message || '')) }
}

onMounted(async () => {
  try { model.value = await getModel(modelId) }
  catch { message.error('模型不存在'); router.push('/models'); return }
  tasksLoading.value = true
  try { const resp = await listTrainingTasks(); trainingTasks.value = resp.tasks.filter((t) => t.model_id === modelId) }
  finally { tasksLoading.value = false }
  evalLoading.value = true
  try { const resp = await listEvaluations(); evalRecords.value = resp.records.filter((r) => r.model_id === modelId) }
  finally { evalLoading.value = false }
})
</script>
