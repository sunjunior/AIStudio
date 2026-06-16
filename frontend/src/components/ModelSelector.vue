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
import { ref, computed, onMounted, watch } from 'vue'
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
  models.value.map((m) => ({ label: `${m.name} (${m.model_type})`, value: m.id }))
)

async function fetchModels() {
  loading.value = true
  try {
    const resp = await listModels(props.modelType, props.onlyReady ? 'ready' : undefined)
    models.value = resp.models
  } catch {
    models.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchModels)
watch(() => props.modelType, fetchModels)
</script>
