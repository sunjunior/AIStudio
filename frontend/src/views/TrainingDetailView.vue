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
        <n-descriptions-item label="状态"><task-status-badge :status="task.status" /></n-descriptions-item>
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
  try { task.value = await getTrainingTask(taskId) }
  catch { message.error('任务不存在'); router.push('/training') }
}

async function fetchLogs() {
  logLoading.value = true
  try { const resp = await getTrainingLogs(taskId); logs.value = resp.logs }
  catch { logs.value = '无法获取日志' }
  finally { logLoading.value = false }
}

onMounted(async () => {
  await fetchTask()
  await fetchLogs()
  if (task.value?.status === 'running') setInterval(fetchLogs, 3000)
})
</script>
