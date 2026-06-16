<template>
  <div>
    <n-page-header>
      <template #title>模型评估</template>
      <template #extra>
        <n-button type="primary" @click="showCreate = true">新建评估</n-button>
      </template>
    </n-page-header>

    <n-data-table :columns="columns" :data="records" :loading="loading" :pagination="{ pageSize: 20 }" style="margin-top: 16px" />

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
  { title: '状态', key: 'status', width: 100, render: (row: EvaluationRecord) => h(TaskStatusBadge, { status: row.status }) },
  { title: '数据集', key: 'dataset', ellipsis: { tooltip: true } },
  { title: '创建时间', key: 'created_at', width: 180 },
  { title: '操作', key: 'actions', width: 80, render: (row: EvaluationRecord) => h(NButton, { size: 'tiny', onClick: () => router.push(`/evaluation/${row.id}`) }, { default: () => '详情' }) },
]

async function fetchRecords() {
  loading.value = true
  try { const resp = await listEvaluations(); records.value = resp.records }
  catch { message.error('获取评估列表失败') }
  finally { loading.value = false }
}

async function handleCreate() {
  if (!form.value.modelId) { message.warning('请选择模型'); return }
  creating.value = true
  try {
    await createEvaluation({ model_id: form.value.modelId, eval_type: form.value.evalType, dataset: form.value.dataset })
    message.success('评估已创建')
    showCreate.value = false
    form.value = { modelId: null, evalType: 'perplexity', dataset: '' }
    await fetchRecords()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally { creating.value = false }
}

onMounted(() => {
  fetchRecords()
  const modelId = route.query.modelId
  if (modelId) { form.value.modelId = Number(modelId); showCreate.value = true }
})
</script>
