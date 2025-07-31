<template>
  <div class="common-layout">
    <header class="main-header">
      <div class="header-title">
        <img src="/logo.svg" alt="logo" class="logo" />
        <h1>AWD FlagCat</h1>
      </div>
      <div class="header-actions">
        <span>暗黑模式</span>
        <el-switch
          v-model="isDark"
          inline-prompt
          :active-icon="Moon"
          :inactive-icon="Sunny"
          style="--el-switch-on-color: #2c2c2c; --el-switch-off-color: #f2f2f2;"
        />
      </div>
    </header>

    <main class="main-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="box-card" shadow="hover">
            <el-tabs v-model="activeTab" class="config-tabs">
              <el-tab-pane label="攻击方法" name="method"></el-tab-pane>
              <el-tab-pane label="目标配置" name="targets"></el-tab-pane>
              <el-tab-pane label="提交设置" name="settings"></el-tab-pane>
            </el-tabs>
            
            <div class="tab-content">
              <Transition name="fade-transform" mode="out-in">
                <component :is="activeComponent" />
              </Transition>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <el-card class="box-card" shadow="hover" :body-style="{ padding: '0px', height: 'calc(100vh - 100px)' }">
             <Dashboard />
          </el-card>
        </el-col>
      </el-row>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ElRow, ElCol, ElCard, ElTabs, ElTabPane, ElSwitch } from 'element-plus';
import { Sunny, Moon } from '@element-plus/icons-vue';
import { useDark } from '@vueuse/core';
import { useLogStore } from './store/logStore';
import { useConfigStore } from './store/configStore';

// 导入所有需要的“主”页面组件
import Dashboard from './components/Dashboard.vue';
import Settings from './views/Settings.vue';
import Targets from './views/Targets.vue';
import AttackMethod from './views/AttackMethod.vue'; 

// --- 暗黑模式逻辑 ---
const isDark = useDark();

// --- Tabs 逻辑 ---
const activeTab = ref('method'); // 默认显示“攻击方法”

// 关键改动 2: 更新组件切换逻辑
const activeComponent = computed(() => {
  switch (activeTab.value) {
    case 'targets':
      return Targets;
    case 'settings':
      return Settings;
    case 'method': // 当Tab为'method'时，显示AttackMethod组件
    default:
      return AttackMethod;
  }
});


// --- 初始化逻辑 ---
const logStore = useLogStore();
const configStore = useConfigStore();

onMounted(() => {
  logStore.connectWebSocket();
  configStore.fetchConfig(); 
});
onUnmounted(() => {
  logStore.disconnectWebSocket();
});
</script>

<style>
/* --- 全局样式 (无 scoped) --- */
:root {
  --app-bg-color: #f0f2f5;
  --card-bg-color: #ffffff;
  --header-bg-color: #ffffff;
  --text-color: #303133;
  --border-color: #e4e7ed;
}

html.dark {
  --app-bg-color: #141414;
  --card-bg-color: #1d1d1d;
  --header-bg-color: #1d1d1d;
  --text-color: #e5e5e5;
  --border-color: #424242;
}

body {
  background-color: var(--app-bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}

.el-card {
  background-color: var(--card-bg-color) !important;
  border: 1px solid var(--border-color) !important;
}
.el-tabs__item {
  color: var(--text-color) !important;
}
.el-tabs__item.is-active {
  color: #409eff !important;
}
.el-tabs__nav-wrap::after {
  background-color: var(--border-color) !important;
}
</style>

<style scoped>
/* --- 局部样式 (有 scoped) --- */
.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: var(--header-bg-color);
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.3s, border-bottom 0.3s;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
}
.logo {
  height: 32px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  padding: 20px;
}

.box-card {
  transition: background-color 0.3s, border-color 0.3s;
}

.tab-content {
  padding-top: 20px;
}

:deep(h2), :deep(h4) {
  margin-top: 0;
  font-size: 16px;
  color: var(--text-color);
}
:deep(p) {
  font-size: 14px;
  color: var(--text-color);
}
:deep(.dashboard) {
  padding: 0;
}
:deep(.log-box) {
  background-color: var(--card-bg-color);
  font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
  height: calc(100vh - 182px);
}
</style>