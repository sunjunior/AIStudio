<template>
  <div>
    <n-page-header>
      <template #title>模型发布</template>
      <template #extra>
        <n-button type="primary" @click="showCreate = true">新建发布</n-button>
      </template>
    </n-page-header>

    <n-data-table :columns="columns" :data="services" :loading="loading" :pagination="{ pageSize: 20 }" style="margin-top: 16px" />

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
  NInput, NInputNumber, NRadio, NRadioGroup, NGrid, NGridItem, NSpace, useMessage,
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
  { title: '类型', key: 'service_type', width: 80, render: (row: PublishedService) => row.service_type === 'api' ? 'API' : '导出' },
  { title: '状态', key: 'status', width: 100, render: (row: PublishedService) => h(TaskStatusBadge, { status: row.status }) },
  { title: '地址/路径', key: 'endpoint', ellipsis: { tooltip: true }, render: (row: PublishedService) => row.service_type === 'api' ? row.endpoint : row.export_path },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 200,
    render: (row: PublishedService) => h(NSpace, null, {
      default: () => [
        row.service_type === 'api' && row.status === 'running'
          ? h(NButton, { size: 'tiny', type: 'warning', onClick: () => handleStop(row.id) }, { default: () => '停止' })
          : null,
        h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDelete(row.id) }, { default: () => '删除' }),
      ],
    }),
  },
]

async function fetchServices() {
  loading.value = true
  try { const resp = await listServices(); services.value = resp.services }
  catch { message.error('获取发布列表失败') }
  finally { loading.value = false }
}

async function handleCreate() {
  if (!form.value.modelId) { message.warning('请选择模型'); return }
  if (form.value.serviceType === 'export' && !form.value.exportPath) { message.warning('请填写导出路径'); return }
  creating.value = true
  try {
    const config: Record<string, any> = {}
    if (form.value.serviceType === 'api') {
      config.port = form.value.port; config.max_tokens = form.value.maxTokens
    } else {
      config.export_path = form.value.exportPath
    }
    await createService({ model_id: form.value.modelId, service_type: form.value.serviceType, config })
    message.success('发布已创建')
    showCreate.value = false
    await fetchServices()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally { creating.value = false }
}

async function handleStop(id: number) {
  try { await stopService(id); message.success('已停止'); await fetchServices() }
  catch { message.error('停止失败') }
}

async function handleDelete(id: number) {
  try { await deleteService(id); message.success('已删除'); await fetchServices() }
  catch { message.error('删除失败') }
}

onMounted(() => {
  fetchServices()
  const modelId = route.query.modelId
  if (modelId) { form.value.modelId = Number(modelId); showCreate.value = true }
})
</script>
