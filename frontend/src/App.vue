<template>
  <n-message-provider>
    <n-dialog-provider>
      <n-notification-provider>
        <n-layout has-sider style="height: 100vh">
          <n-layout-sider
            bordered
            collapse-mode="width"
            :collapsed-width="64"
            :width="200"
            :collapsed="collapsed"
            show-trigger
            @collapse="collapsed = true"
            @expand="collapsed = false"
          >
            <div class="logo">
              <n-icon size="28" v-if="collapsed">
                <flash-outline />
              </n-icon>
              <span v-else style="font-weight: 700; font-size: 18px">AIStudio</span>
            </div>
            <n-menu
              :collapsed="collapsed"
              :collapsed-width="64"
              :collapsed-icon-size="22"
              :value="activeKey"
              :options="menuOptions"
              @update:value="handleMenuSelect"
            />
          </n-layout-sider>
          <n-layout>
            <n-layout-content style="padding: 24px; overflow-y: auto">
              <router-view />
            </n-layout-content>
          </n-layout>
        </n-layout>
      </n-notification-provider>
    </n-dialog-provider>
  </n-message-provider>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NIcon, NLayout, NLayoutSider, NMenu,
  NMessageProvider, NDialogProvider, NNotificationProvider,
} from 'naive-ui'
import { CubeOutline, FlashOutline, FlaskOutline, RocketOutline } from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const activeKey = computed(() => route.path)

const menuOptions = [
  { label: '模型管理', key: '/models', icon: () => h(NIcon, null, { default: () => h(CubeOutline) }) },
  { label: '模型训练', key: '/training', icon: () => h(NIcon, null, { default: () => h(FlashOutline) }) },
  { label: '模型评估', key: '/evaluation', icon: () => h(NIcon, null, { default: () => h(FlaskOutline) }) },
  { label: '模型发布', key: '/publishing', icon: () => h(NIcon, null, { default: () => h(RocketOutline) }) },
]

function handleMenuSelect(key: string) {
  router.push(key)
}
</script>

<style>
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
.logo { display: flex; align-items: center; justify-content: center; height: 64px; border-bottom: 1px solid #efefef; }
</style>
