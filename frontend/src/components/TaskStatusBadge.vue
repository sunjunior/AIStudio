<template>
  <n-tag :type="tagType" size="small">
    {{ statusLabel }}
  </n-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NTag } from 'naive-ui'

const props = defineProps<{ status: string }>()

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
