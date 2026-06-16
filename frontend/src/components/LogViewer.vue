<template>
  <div class="log-viewer">
    <div class="log-header">
      <span class="log-title">日志输出</span>
      <n-space size="small">
        <n-button size="tiny" @click="autoScroll = !autoScroll">
          {{ autoScroll ? '暂停滚动' : '自动滚动' }}
        </n-button>
        <n-button size="tiny" @click="emit('refresh')">刷新</n-button>
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

const props = defineProps<{ logs: string; loading?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()

const autoScroll = ref(true)
const logRef = ref<InstanceType<typeof NInput> | null>(null)

watch(() => props.logs, async () => {
  if (autoScroll.value) {
    await nextTick()
    const textarea = logRef.value?.$el?.querySelector('textarea')
    if (textarea) textarea.scrollTop = textarea.scrollHeight
  }
})
</script>

<style scoped>
.log-viewer { border: 1px solid #e0e0e0; border-radius: 4px; overflow: hidden; }
.log-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; }
.log-title { font-weight: 600; font-size: 13px; }
</style>
