<template>
  <div>
    <n-page-header>
      <template #title>模型管理</template>
      <template #extra>
        <n-button type="primary" @click="showCreateModal = true">导入模型</n-button>
      </template>
    </n-page-header>

    <n-data-table
      :columns="columns"
      :data="models"
      :loading="loading"
      :pagination="{ pageSize: 20 }"
      style="margin-top: 16px"
    />

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
          <n-button type="primary" :loading="creating" @click="handleCreate">确认导入</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton, NDataTable, NPageHeader, NModal, NForm, NFormItem,
  NInput, NRadio, NRadioGroup, NSpace, useMessage,
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
    title: '类型', key: 'model_type', width: 130,
    render: (row: Model) =>
      ({ llm: 'LLM', embedding: 'Embedding', peft_checkpoint: 'LoRA 适配器' }[row.model_type] ?? row.model_type),
  },
  {
    title: '来源', key: 'source', width: 100,
    render: (row: Model) => ({ huggingface: 'HF', local: '本地', uploaded: '上传' }[row.source] ?? row.source),
  },
  {
    title: '状态', key: 'status', width: 100,
    render: (row: Model) => h(TaskStatusBadge, { status: row.status }),
  },
  { title: '来源路径', key: 'source_path', ellipsis: { tooltip: true } },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 220,
    render: (row: Model) =>
      h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'tiny', onClick: () => router.push(`/models/${row.id}`) }, { default: () => '详情' }),
          row.source === 'huggingface' && row.status === 'ready'
            ? h(NButton, { size: 'tiny', onClick: () => handleDownload(row.id) }, { default: () => '下载' })
            : null,
          h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDelete(row.id) }, { default: () => '删除' }),
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
