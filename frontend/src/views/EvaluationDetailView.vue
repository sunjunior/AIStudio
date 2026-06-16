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
        <n-descriptions-item label="状态"><task-status-badge :status="record.status" /></n-descriptions-item>
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
        <n-descriptions-item v-for="(value, key) in record.metrics" :key="key" :label="key">
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
  try { record.value = await getEvaluation(recordId) }
  catch { message.error('评估记录不存在'); router.push('/evaluation') }
}

async function fetchLogs() {
  logLoading.value = true
  try { const resp = await getEvaluationLogs(recordId); logs.value = resp.logs }
  catch { logs.value = '无法获取日志' }
  finally { logLoading.value = false }
}

onMounted(async () => {
  await fetchRecord()
  await fetchLogs()
  if (record.value?.status === 'running') setInterval(fetchLogs, 3000)
})
</script>
