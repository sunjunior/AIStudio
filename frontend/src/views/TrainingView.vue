<template>
  <div>
    <n-page-header>
      <template #title>模型训练</template>
      <template #extra>
        <n-button type="primary" @click="showCreate = true">新建训练</n-button>
      </template>
    </n-page-header>

    <n-data-table :columns="columns" :data="tasks" :loading="loading" :pagination="{ pageSize: 20 }" style="margin-top: 16px" />

    <n-modal v-model:show="showCreate" preset="card" title="新建训练任务" style="width: 600px">
      <n-form label-placement="top">
        <n-form-item label="选择模型" required>
          <model-selector v-model="form.modelId" model-type="llm" :only-ready="true" />
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
  NInput, NInputNumber, NRadio, NRadioGroup, NGrid, NGridItem, NSpace, useMessage,
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
  { title: '状态', key: 'status', width: 100, render: (row: TrainingTask) => h(TaskStatusBadge, { status: row.status }) },
  { title: '开始时间', key: 'started_at', width: 180 },
  { title: '完成时间', key: 'finished_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 120,
    render: (row: TrainingTask) => h(NSpace, null, {
      default: () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/training/${row.id}`) }, { default: () => '详情' }),
        row.status === 'running'
          ? h(NButton, { size: 'tiny', type: 'warning', onClick: () => handleCancel(row.id) }, { default: () => '取消' })
          : null,
      ],
    }),
  },
]

async function fetchTasks() {
  loading.value = true
  try { const resp = await listTrainingTasks(); tasks.value = resp.tasks }
  catch { message.error('获取训练任务列表失败') }
  finally { loading.value = false }
}

async function handleCreate() {
  if (!form.value.modelId) { message.warning('请选择模型'); return }
  creating.value = true
  try {
    await createTrainingTask({
      model_id: form.value.modelId,
      config: {
        method: form.value.method, learning_rate: form.value.learningRate,
        num_epochs: form.value.epochs, batch_size: form.value.batchSize,
        lora_r: form.value.loraR, lora_alpha: form.value.loraAlpha,
        max_length: form.value.maxLength, dataset_path: form.value.datasetPath,
        output_name: form.value.outputName,
      },
    })
    message.success('训练任务已创建')
    showCreate.value = false
    await fetchTasks()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.response?.data?.detail || e?.message || ''))
  } finally { creating.value = false }
}

async function handleCancel(id: number) {
  try {
    const { cancelTrainingTask } = await import('../api/training')
    await cancelTrainingTask(id)
    message.success('已取消')
    await fetchTasks()
  } catch { message.error('取消失败') }
}

onMounted(() => {
  fetchTasks()
  const modelId = route.query.modelId
  if (modelId) { form.value.modelId = Number(modelId); showCreate.value = true }
})
</script>
